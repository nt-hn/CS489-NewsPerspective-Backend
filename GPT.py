from dotenv import load_dotenv
from openai import OpenAI
import requests

class GPTCompareArticles:
    def __init__(self, OPENAI_API_KEY):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def compare_articles(self, article_1: str, article_2: str) -> str:
        try:
            model = "gpt-4o-mini"
            conversation_history = [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
            
            prompt_article_one = f"You are News Perspective a company that looks for articles online and compare their factual analysis. Your task is to compare the facts of two articles the articles the user is currently reading and other articles in the market. Output summary of your analysis, instead of first article use the term current article and instead of second article use the term other articles. Keep your response as concise as possible. I will give you what other articles are saying in the next prompt but here is the article the user is currently reading: `{article_1}`"
            conversation_history.append({"role": "user", "content": prompt_article_one})
            response = self.client.chat.completions.create(
                model=model,
                messages=conversation_history
            )
            output = response.choices[0].message.content.strip()

            conversation_history.append({"role": "assistant", "content": output})
            
            prompt_article_two = f"Here is what other articles are saying {article_2}"
            conversation_history.append({"role": "user", "content": prompt_article_two})
            response = self.client.chat.completions.create(
                model=model,
                messages=conversation_history
            )
            result = response.choices[0].message.content.strip()

            return result
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

if __name__ == '__main__':
    article_1 = """
    Proponents of strong climate change policies argue that immediate and aggressive action is essential to avert catastrophic global warming. With rising temperatures, extreme weather events, and the growing toll of natural disasters, the need for comprehensive climate action is clearer than ever. Advocates support measures like rejoining the Paris Agreement, pushing for a Green New Deal, and implementing carbon taxes or emissions regulations to transition away from fossil fuels.

Key Points:

Environmental Crisis: Unchecked climate change is leading to more frequent and severe weather events such as wildfires, hurricanes, and droughts, which are already having devastating consequences for communities worldwide.
Economic Opportunities: Investing in clean energy technologies like solar, wind, and electric vehicles can create millions of new jobs, boosting the economy while combating climate change.
Moral Imperative: The longer the U.S. delays action, the more costly and difficult it becomes to reverse the damage. Ignoring climate change disproportionately harms low-income and minority communities, who are often the most vulnerable.
    """
    article_2 = """
    Critics of aggressive climate policies argue that sweeping regulations are often driven by political agendas rather than genuine environmental needs. They caution that drastic climate action could harm the economy, lead to job losses, especially in industries like oil, coal, and natural gas, and increase energy costs for average Americans. Instead, they argue for a more measured approach that balances environmental concerns with economic growth and energy security.

Key Points:

Economic Risks: A rapid transition to green energy could cause economic disruptions, particularly in fossil fuel-dependent states, leading to job losses and decreased energy security. Energy prices could rise, affecting families and businesses.
Technological Optimism: Rather than government mandates, market-driven innovation and technological advancements can provide solutions to environmental challenges without the need for heavy regulation.
Skepticism About Science: While climate change is real, critics argue that the data isn't conclusive enough to justify the immediate and extreme measures proposed. Some question the reliability of climate models and argue that the focus should be on adaptation rather than drastic prevention.
    """
