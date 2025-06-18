import os

from dotenv import load_dotenv
from autogen.agentchat import initiate_group_chat
from autogen.agentchat.group import RevertToUserTarget, OnCondition, StringLLMCondition, AgentTarget
from autogen.agentchat.group.patterns import DefaultPattern
from autogen import ConversableAgent, LLMConfig, UserProxyAgent
from util.rental_database import (
  find_customer_by_email, 
  find_film_by_title, 
  find_films_with_similar_title, 
  rent_film,
  get_customer_rental_history
)

# Load environment variables from a .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Initialize LLM configuration
llm_config = LLMConfig(
  api_type="openai", 
  model="gpt-4o-mini",
  api_key=os.getenv("OPENAI_API_KEY"),
)

# Create an agent for rental services
rental_agent_behavior = """
  You are a rental agent that helps users find rental films and customers as well as rent out films.
  You can search for films by title, find customers by email, and assist with renting films.
  When renting out films, you will need to check if the film exists.
  If the film does not exist, you will inform the user that the film is not available and find films with similar titles and recommend it to them.
  If the film exists, you will check if the customer exists by their email address.
  If the customer does not exist, you will inform the user that the customer is not registered and ask them to register first.
  If the customer exists, you will proceed to rent out the film to the customer after confirming with them about the price.
  You will also handle cases where the film is already rented out and inform the user accordingly.
  You should respond to user queries in a helpful and informative manner.

  You should display film in the table format
"""

rental_agent = ConversableAgent(
    name="rental_agent",
    description="An agent that helps users find rental films and customers as well as rent out films.",
    llm_config=llm_config,
    system_message=rental_agent_behavior,
    functions=[
      find_customer_by_email,
      find_film_by_title,
      find_films_with_similar_title,
      rent_film,
      ],
)

history_agent_behavior = """
  You are a history agent that provides customers with their rental histories.
  Based on the customer's email, you will retrieve their rental history from the database.
  If the customer does not exist, you will inform the user that the customer is not registered.
  If the customer exists, you will provide a summary of their rental history.
  You should respond to user queries in a helpful and informative manner.
"""

history_agent = ConversableAgent(
    name="history_agent",
    description="An agent that provides customers with their rental histories.",
    llm_config=llm_config,
    system_message=history_agent_behavior,
    functions=[
      find_customer_by_email,
      get_customer_rental_history
    ],
)

user = UserProxyAgent(
  name="Customer",
  system_message="Agent that represents the Customer",
  code_execution_config=False,
);


# Start the conversation with the rental agent

rental_agent.handoffs.add_llm_conditions([
  OnCondition(
    target=AgentTarget(history_agent),
    condition=StringLLMCondition("When the user asks for their rental history")
  )
])

history_agent.handoffs.add_llm_conditions([
  OnCondition(
    target=AgentTarget(rental_agent),
    condition=StringLLMCondition("When the user asks for a film rental")
  )
])

agent_pattern = DefaultPattern(
  agents=[rental_agent, history_agent],
  user_agent=user,
  initial_agent=rental_agent,
  group_after_work=RevertToUserTarget(),
)

group_chat = initiate_group_chat(
    pattern=agent_pattern,
    messages="Hello",
    max_rounds=50,
)