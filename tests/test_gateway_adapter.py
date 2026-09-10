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
                "usage": {"prompt_tokens": 120, "completion_tokens": 30},
                "gateway": {
                    "provider": "mock", "model": "demo", "cost_usd": 0.0012,
                    "pricing_known": True, "routing_policy": "priority",
                    "attempts": [{"target": "mock:demo", "status": "success"}]
                },
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
        observation = client.usage_observations()[-1]
        self.assertEqual(observation["usage"]["prompt_tokens"], 120)
        self.assertEqual(observation["usage"]["completion_tokens"], 30)
        self.assertEqual(observation["gateway"]["provider"], "mock")
        self.assertEqual(observation["gateway"]["model"], "demo")
        self.assertEqual(observation["gateway"]["cost_usd"], 0.0012)


if __name__ == "__main__":
    unittest.main()
