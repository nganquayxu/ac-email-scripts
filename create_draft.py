"""Create a draft campaign and optionally send a test.

Example:
  python3 create_draft.py --name "Oct promo" --subject "Hello" \
      --html-file email.html --from-email me@example.com --from-name "Me" \
      --list-id 1 --test-to me@example.com
"""
import argparse
import re

import ac


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True, help="internal campaign name")
    p.add_argument("--subject", required=True)
    p.add_argument("--html-file", required=True)
    p.add_argument("--text-file", help="plain-text version (default: HTML stripped)")
    p.add_argument("--from-email", required=True)
    p.add_argument("--from-name", required=True)
    p.add_argument("--reply-to")
    p.add_argument("--list-id", type=int, required=True)
    p.add_argument("--test-to", help="send a test to this address after creating")
    a = p.parse_args()

    html = open(a.html_file, encoding="utf-8").read()
    if a.text_file:
        text = open(a.text_file, encoding="utf-8").read()
    else:
        text = re.sub(r"<[^>]+>", "", html).strip()

    campaign_id, message_id = ac.create_draft(
        a.name, a.subject, html, text, a.from_email, a.from_name, a.list_id, a.reply_to
    )
    print(f"Draft created: campaign_id={campaign_id} message_id={message_id}")

    if a.test_to:
        print(ac.send_test(campaign_id, message_id, a.subject, a.test_to))


if __name__ == "__main__":
    main()
