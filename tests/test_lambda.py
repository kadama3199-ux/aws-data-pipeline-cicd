import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../lambda")
    )
)

from lambda_function import lambda_handler


class TestLambdaFunction:

    @patch("lambda_function.table")
    def test_duplicate_file(self, mock_table):

        # DynamoDB says file was already processed
        mock_table.get_item.return_value = {
            "Item": {
                "pipeline_id": "orders",
                "last_file": "orders/emp.txt",
                "status": "SUCCESS"
            }
        }

        event = {
            "Records": [
                {
                    "body": json.dumps({
                        "Records": [
                            {
                                "s3": {
                                    "bucket": {
                                        "name": "demopipelines3"
                                    },
                                    "object": {
                                        "key": "orders/emp.txt"
                                    }
                                }
                            }
                        ]
                    })
                }
            ]
        }

        response = lambda_handler(event, {})

        assert response["statusCode"] == 200
        assert response["message"] == "File processed successfully"

        mock_table.get_item.assert_called_once()


if __name__ == "__main__":
    import pytest
    pytest.main()
