from skills.calculator import Calculator


class DecisionEngine:

    def __init__(self, skills):

        self.skills = skills


    def process(self, message):

        message = message.lower().strip()


        # Greeting
        if "hello" in message or "hi" in message:

            return "Hello, I am AZAD."


        # Calculator - Addition
        elif "add" in message:

            try:

                numbers = message.split()

                a = int(numbers[-2])
                b = int(numbers[-1])

                calculator = self.skills.get_skill("calculator")

                result = calculator.add(a, b)

                return f"The answer is {result}"


            except:

                return "Please write like: add 5 10"



        # Calculator - Multiplication
        elif "multiply" in message:

            try:

                numbers = message.split()

                a = int(numbers[-2])
                b = int(numbers[-1])

                calculator = self.skills.get_skill("calculator")

                result = calculator.multiply(a, b)

                return f"The answer is {result}"


            except:

                return "Please write like: multiply 5 10"



        # Save Note
        elif "save note" in message:

            try:

                text = message.replace("save note", "").strip()

                notes = self.skills.get_skill("notes")

                return notes.save(text)


            except:

                return "I could not save the note."



        # Show Notes
        elif "show notes" in message:

            try:

                notes = self.skills.get_skill("notes")

                return notes.read()


            except:

                return "I could not read notes."



        else:

            return "I don't know this yet."