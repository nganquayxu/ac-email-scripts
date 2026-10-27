"""Send a test of an existing campaign.

Example:
  python3 send_test.py --campaign-id 12 --message-id 34 --subject "Test" --to me@example.com
"""
import argparse

import ac

p = argparse.ArgumentParser()
p.add_argument("--campaign-id", type=int, required=True)
p.add_argument("--message-id", type=int, required=True)
p.add_argument("--subject", required=True)
p.add_argument("--to", required=True)
a = p.parse_args()

print(ac.send_test(a.campaign_id, a.message_id, a.subject, a.to))
