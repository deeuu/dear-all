# dear-all

Email a lot of people with ease:

1. Write your message, e.g. `message.txt`
2. Include your a csv file with the same structure as `names.csv`
3. Fill in `configuration.json`
4. Fire away:
    ```python
    python dear_all.py -i configuration.json
    ```
Implementation based on [Erik Reed's
post](https://erikreed.net/batch-emailing-a-csv-file-of-data-using-python-and-smtp/)
and [mass-mailer](https://github.com/cfedermann/mass-mailer)
