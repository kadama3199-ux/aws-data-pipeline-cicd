import sys
import os
import json
import unittest

# Add lambda directory to sys.path so lambda_function can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lambda')))

from lambda_function import lambda_handler

class TestLambdaFunction(unittest.TestCase):

    def test_lambda_handler_success(self):
        event = {"records": [{"id": 1, "name": "record_1"}, {"id": 2, "name": "record_2"}]}
        context = {}
        
        response = lambda_handler(event, context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["message"], "Data pipeline processed successfully!")
        self.assertEqual(body["records_processed"], 2)

    def test_lambda_handler_empty_event(self):
        event = {}
        context = {}
        
        response = lambda_handler(event, context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["records_processed"], 0)

if __name__ == '__main__':
    unittest.main()
