import json
import unittest
from unittest.mock import MagicMock, patch

from etl_intelligence.gateway import OpenAICompatibleGatewayClient


class OpenAICompatibleGatewayClientTest(unittest.TestCase):
    @patch("etl_intelligence.gateway.request.urlopen")
    def test_uses_current_gateway_chat_contract_and_default_model(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {"pipeline_summary": {"text": "synthetic"}}
                            )
                        }
                    }
                ]
            }
        ).encode("utf-8")
        urlopen.return_value = response

        client = OpenAICompatibleGatewayClient(
            base_url="https://gateway.example.invalid",
            api_key="synthetic-key",
        )
        result = client("system", '{"normalized_metadata":{}}')

        request_obj = urlopen.call_args.args[0]
        payload = json.loads(request_obj.data.decode("utf-8"))

        self.assertEqual(
            request_obj.full_url,
            "https://gateway.example.invalid/v1/chat/completions",
        )
        self.assertEqual(request_obj.get_header("X-api-key"), "synthetic-key")
        self.assertEqual(payload["model"], "default")
        self.assertFalse(payload["stream"])
        self.assertEqual(
            payload["messages"][1]["content"],
            '{"normalized_metadata":{}}',
        )
        self.assertEqual(
            result,
            {"pipeline_summary": {"text": "synthetic"}},
        )


if __name__ == "__main__":
    unittest.main()
