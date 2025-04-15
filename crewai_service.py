import os
from textwrap import dedent

from crewai import Agent, Crew, Task
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from django.conf import settings

class FileTools:
    @tool("Write File with content")
    def write_file(data: str):
        """Useful to write a file to a given path with a given content. 
           The input to this tool should be a pipe (|) separated text 
           of length two, representing the full path of the file, 
           including the ./lore/, and the written content you want to write to it.
        """
        try:
            path, content = data.split("|")
            path = path.replace("\n", "").replace(" ", "").replace("", "")
            if not path.startswith("./lore"):
                path = f"./lore/{path}"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, "w") as f:
                f.write(content)
            return f"File written to {path}."
        except Exception as e:
            return f"Error with the input format for the tool: {str(e)}"

class CreateTasks:
    @staticmethod
    def expand_idea():
        return {
            "description": """Analyse the given task and prepare comprehensive pin-points
                for accomplishing it. Make sure the ideas are to the point, coherent, and compelling.
                
                RULES:
                - Write ideas in bullet points.
                - Avoid adult ideas.
                
                Task to analyze: {idea}
            """,
            "expected_output": """A detailed bullet-point list of ideas and concepts to be developed,
                formatted in a clear and organized manner."""
        }
    
    @staticmethod
    def write():
        return {
            "description": """Write a compelling story in 1200 words based on the blueprint 
                ideas provided by the Idea analyst.
                Make sure the contents are coherent, easily communicable, and captivating.
                
                RULES:
                - Writing must be grammatically correct.
                - Use as little jargon as possible
            """,
            "expected_output": """A well-written, engaging story of approximately 1200 words
                that incorporates all the key ideas from the blueprint."""
        }
    
    @staticmethod
    def edit():
        return {
            "description": """Look for any grammatical mistakes, edit, and format if needed.
                Add title and subtitles to the text when needed.
                Do not shorten the content or add comments.
                Create a suitable filename for the content with the .txt extension.
                You MUST use the tool to save it to the path ./lore/(your title.txt).
            """,
            "expected_output": """A polished, error-free version of the text with proper formatting,
                titles, and subtitles, saved to a file in the ./lore directory."""
        }

class CrewAIService:
    def __init__(self):
        # Initialize LLM with OpenAI
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )
        
        # Initialize agents
        self.idea_analyst = Agent(
            role="Idea Analyst",
            goal="Comprehensively analyse an idea to prepare blueprints for the article to be written",
            backstory="""You are an experienced content analyst, well versed in analyzing 
            an idea and preparing a blueprint for it.""",
            llm=self.llm,
            verbose=True
        )
        
        self.writer = Agent(
            role="Fiction Writer",
            goal="Write compelling fantasy and sci-fi fictions from the ideas given by the analyst",
            backstory="""A renowned fiction-writer with 2 times NYT 
            a best-selling author in the fiction and sci-fi category.""",
            llm=self.llm,
            verbose=True
        )
        
        self.editor = Agent(
            role="Content Editor",
            goal="Edit contents written by writer",
            backstory="""You are an experienced editor with years of 
            experience in editing books and stories.""",
            llm=self.llm,
            tools=[FileTools.write_file],
            verbose=True
        )
    
    def generate_content(self, idea):
        # Ensure lore directory exists
        lore_dir = os.path.join(settings.BASE_DIR, "lore")
        if not os.path.exists(lore_dir):
            os.makedirs(lore_dir)
        
        # Create tasks with proper configuration
        expand_idea_task = Task(
            description=CreateTasks.expand_idea()["description"].format(idea=idea),
            expected_output=CreateTasks.expand_idea()["expected_output"],
            agent=self.idea_analyst
        )
        
        write_task = Task(
            description=CreateTasks.write()["description"],
            expected_output=CreateTasks.write()["expected_output"],
            agent=self.writer,
            context=expand_idea_task.output if hasattr(expand_idea_task, 'output') else None
        )
        
        edit_task = Task(
            description=CreateTasks.edit()["description"],
            expected_output=CreateTasks.edit()["expected_output"],
            agent=self.editor,
            context=write_task.output if hasattr(write_task, 'output') else None
        )
        
        # Create crew
        crew = Crew(
            tasks=[expand_idea_task, write_task, edit_task],
            agents=[self.idea_analyst, self.writer, self.editor],
            verbose=True
        )
        
        # Execute crew
        result = crew.kickoff()
        
        return result

