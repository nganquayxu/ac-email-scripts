# ac-email-scripts

Create draft email campaigns in ActiveCampaign and send test emails. Python 3, no dependencies.

## Setup

Set two environment variables (or put them in a local `.env`, which is git-ignored):

```
AC_API_URL=https://youraccount.api-us1.com
AC_API_KEY=your_api_key
```

On claude.ai/code, set them in the environment's variables and allow outbound access to your `*.api-us1.com` domain.

## Use

```
python3 create_draft.py --name "Oct promo" --subject "Hello" --html-file email.html \
    --from-email me@example.com --from-name "Me" --list-id 1 --test-to me@example.com

python3 send_test.py --campaign-id 12 --message-id 34 --subject "Test" --to me@example.com
```

## Notes

- Everything uses API v3: `POST /campaign`, `POST /messages`, `POST /campaignMessages`, `PUT /campaigns/{id}/edit`, `POST /campaigns/test-send`. Campaigns are never scheduled, so they stay drafts.
- Test sends need a verified sending domain and are rate limited; trial accounts can only send tests to the account owner's address.
- Prefix `--to` with `+` to send through the regular mail server instead of the test server.
