GOAL
Our Python program will fetch stock prices for selected stocks, such as Tesla, using APIs. For example, it will retrieve the closing price for March 10th and compare it to March 9th to calculate the price difference and direction.

Calculating the percentage change helps quantify the price movement. For instance, a $100 increase from March 9th to March 10th might represent a 10% rise.

When the price difference exceeds a defined threshold, such as 10%, the program will fetch relevant news to explain the fluctuation. This might include product launches or factory acquisitions indicating positive company developments.

After detecting significant price changes and retrieving news, the program will send an SMS alert via Twilio. This message will summarize the price fluctuation and provide relevant news, enabling timely trading decisions.

The goal is to receive messages like this each morning, informing you of major Tesla stock fluctuations and associated news to help decide whether to buy or sell shares.

Key Takeaways
Built a stock news monitoring project inspired by Bloomberg terminals.
Learned to fetch and compare stock closing prices using APIs.
Integrated news retrieval based on significant stock price fluctuations.
Implemented SMS alerts via Twilio for timely stock market updates.

CHALLENGES
Created a formatted list of article headlines and descriptions using list comprehension.
Integrated Twilio API to send SMS messages containing news articles.
Enhanced messages with stock movement indicators using emojis and rounded percentages.
Demonstrated practical improvements for stock alert notifications via SMS.