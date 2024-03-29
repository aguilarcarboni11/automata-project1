class State:
    def __init__(self, name):
        self.name = name
        self.transitions = {}

class Automaton:
    def __init__(self):
        self.states = {}
        self.alphabet = set()
        self.start_state = None
        self.accept_states = set()

    def print_fa(self):
        print("Alphabet:", self.alphabet)
        print("States:", list(self.states.keys()))
        print("Start State:", self.start_state)
        print("Accept States:", list(self.accept_states))
        print("Transitions:")
        
        if isinstance(self, NFA):
            for state, state_obj in self.states.items():
                for symbol, transitions in state_obj.transitions.items():
                    if symbol != "epsilon_transitions":
                        if isinstance(transitions, list):
                            for transition in transitions:
                                input_symbol = transition.input_symbol if transition.input_symbol != "<EPSILON>" else "epsilon"
                                print(f"From {state} to {transition.next_state} with symbol {input_symbol}")
                        else:
                            input_symbol = transitions.input_symbol if transitions.input_symbol != "<EPSILON>" else "epsilon"
                            print(f"From {state} to {transitions.next_state} with symbol {input_symbol}")
                    else:
                        for next_state in transitions:
                            print(f"From {state} to {next_state} with symbol epsilon")
        else:
            for state, state_obj in self.states.items():
                for symbol, next_states in state_obj.transitions.items():
                    if isinstance(next_states, list):
                        for next_state in next_states:
                            print(f"From {state} to {next_state} with symbol {symbol}")
                    else:
                        print(f"From {state} to {next_states} with symbol {symbol}")           
                        
    def add_state(self, name):
        if name not in self.states:
            self.states[name] = State(name)

    def add_transition(self, current_state, input_symbol, next_state):
        self.states[current_state].transitions[input_symbol] = next_state
        self.alphabet.add(input_symbol)

    def set_start_state(self, start_state):
        self.start_state = start_state

    def set_accept_states(self, accept_states):
        self.accept_states = set(accept_states)

class DFA(Automaton):
    def process_string(self, input_string, verbose = False):
        current_state = self.start_state

        # Track the path for verbose mode
        path = []

        # Check symbol by symbol ensuring each is in the alphabet and has a next state
        for symbol in input_string:
            if symbol not in self.alphabet:
                if verbose:
                    return "REJECT", f"Invalid symbol '{symbol}'", path
                else:
                    return "REJECT", f"Invalid symbol '{symbol}'"

            next_state = self.states[current_state].transitions.get(symbol)
            if next_state is None:
                if verbose:
                    return "REJECT", f"No transition for '{symbol}' in state '{current_state}'", path
                else:
                    return "REJECT", f"No transition for '{symbol}' in state '{current_state}'"


            path.append((current_state, symbol, next_state))
            current_state = next_state

        # Check if current state is final state and finish process
        if current_state in self.accept_states:
            if verbose:
                return "ACCEPT", "String accepted", path
            else:
                return "ACCEPT", "String accepted"
        else:
            if verbose:
                return "REJECT", "String rejected", path
            else:
                return "REJECT", "String rejected"


class NFA(Automaton):
    def __init__(self):
        super().__init__()

    def add_transition(self, current_state, input_symbol, next_state):
        transition = NFATransition(current_state, input_symbol, next_state)
        if current_state not in self.states:
            self.states[current_state] = State(current_state)

        if input_symbol == "<EPSILON>":
            if "epsilon_transitions" not in self.states[current_state].transitions:
                self.states[current_state].transitions["epsilon_transitions"] = []
            self.states[current_state].transitions["epsilon_transitions"].append(next_state)
        else:
            if "transitions" not in self.states[current_state].transitions:
                self.states[current_state].transitions["transitions"] = []
            self.states[current_state].transitions["transitions"].append(transition)
        
        self.alphabet.add(input_symbol)

    def process_string(self, input_string, current_state, verbose=False, path=None):
        # Track the path for verbose mode
        if path is None:
            path = []

        if not input_string:
            if current_state in self.accept_states:
                if verbose:
                    return "ACCEPT", "String accepted", path
                else:
                    return "ACCEPT", "String accepted"
            else:
                if verbose:
                    return "REJECT", "String rejected", path
                else:
                    return "REJECT", "String rejected"

        symbol = input_string[0]
        remaining_input = input_string[1:]

        if current_state not in self.states:
            return "REJECT", f"Invalid state '{current_state}'"

        transitions = self.states[current_state].transitions.get("transitions", [])
        epsilon_transitions = self.states[current_state].transitions.get("epsilon_transitions", [])

        final_path = []  # initialize final_path variable

        for transition in transitions:
                if transition.input_symbol == symbol:
                    if verbose: 
                        new_path = path + [(current_state, symbol, transition.next_state)]
                        result, message, final_path = self.process_string(remaining_input, transition.next_state, verbose, new_path)
                        if result == "ACCEPT":
                            return result, message, final_path
                    else:
                        new_path = path + [(current_state, symbol, transition.next_state)]
                        result, message = self.process_string(remaining_input, transition.next_state)
                        if result == "ACCEPT":
                            return result, message

        for next_state in epsilon_transitions:
            if verbose:
                if (next_state, "<EPSILON>", next_state) in path:
                    continue  # Avoid infinite loop
                new_path = path + [(current_state, "<EPSILON>", next_state)]
                result, message, final_path = self.process_string(input_string, next_state, verbose, new_path)
                if result == "ACCEPT":
                    return result, message, final_path
            else:
                if (next_state, "<EPSILON>", next_state) in path:
                    continue  # Avoid infinite loop
                new_path = path + [(current_state, "<EPSILON>", next_state)]
                result, message = self.process_string(input_string, next_state, verbose, new_path)
                if result == "ACCEPT":
                    return result, message

        if verbose:
            return "REJECT", f"No transition for '{symbol}' in state '{current_state}'", path
        else:
            return "REJECT", f"No transition for '{symbol}' in state '{current_state}'"

class NFATransition:
    def __init__(self, state, input_symbol, next_state):
        self.state = state
        self.input_symbol = input_symbol
        self.next_state = next_state