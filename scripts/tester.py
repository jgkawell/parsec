import random

from parsec.tree import Node, Tree


_CONSTRAINTS_FILE = '/constraints.yml'
_PARAMETERS_FILE = '/parameters.yml'

# Python 2.7 compatibility
try:
    input = raw_input
except NameError:
    pass


def run(input):
    # Extract input values (passed this way for multiprocessing)
    processor = input[0]
    mode = input[1]
    output_dir = input[2]
    config_dir = input[3]
    faults = input[4]
    test_type = input[5]
    questions_asked = {}

    # Create tree
    tree = Tree()
    tree.build(config_dir + _CONSTRAINTS_FILE, config_dir + _PARAMETERS_FILE)

    # Iterate through sentences
    for fault in faults:
        current_count = 0

        # Reset tree scores
        for key, node in tree.nodes.items():
            node.score = 0.0

        fault_id = fault['id']
        correct_params = fault['constraints']
        sentence = fault['description']

        if mode == "manual":
            print('-' * 50)
            print("Fault: {}".format(fault_id))
            print("Sentence: {}".format(sentence))

        # Different testing setups
        if test_type == "nlp":
            question_nodes = setup_nlp(processor, sentence, tree)
        elif test_type == "tree":
            question_nodes = setup_tree(tree)
        elif test_type == "tree_nlp":
            question_nodes = setup_tree_nlp(processor, sentence, tree)
        else:
            raise ValueError("Invalid test type: {}".format(test_type))

        # Iterate over all questions to ask
        corrected, current_count, response, params = iterate_over_nodes(mode, tree, question_nodes, correct_params, current_count)

        # If no correction can be found in tree
        if not corrected:
            print("Couldn't find a correction. Try rephrasing your feedback?")
            print(fault)

        if mode == "manual":
            print("Total questions asked: {}".format(current_count))
            print("Parameters: {}".format(params))
            print("Followup response: {}".format(response))

        questions_asked[fault_id] = current_count

    return questions_asked


def setup_nlp(processor, sentence, tree):
    # Get the word similarity scores for working dictionary
    word_similarity_scores = processor.process_input(sentence)

    # Score each node in the tree based of word similarity score
    tree.score_tree(word_similarity_scores)

    # Create question nodes from all leaves
    question_nodes = []
    for node in tree.nodes.values():
        if node.leaf:
            question_nodes.append(node)

    # Randomize before sorting by score
    random.shuffle(question_nodes)

    # Sort nodes
    question_nodes = sorted(question_nodes, key=lambda x: x.score, reverse=True)

    return question_nodes


def setup_tree(tree):
    # Get root of tree
    root = tree.nodes[('root')]

    # Pull out all questions (not ranked)
    question_nodes = []
    for child in root.children:
        question_nodes.append(tree.nodes[child])

    # Randomize order
    random.shuffle(question_nodes)

    return question_nodes


def setup_tree_nlp(processor, sentence, tree):
    # Get the word similarity scores for working dictionary
    word_similarity_scores = processor.process_input(sentence)

    # Score each node in the tree based of word similarity score
    tree.score_tree(word_similarity_scores)

    # Get best question to ask from scored tree
    question_nodes = tree.get_questions()

    return question_nodes


def iterate_over_nodes(mode, tree, question_nodes, correct_params, total_questions_asked):
    # Display question that will be asked
    corrected = False
    for node in question_nodes:
        # Recursively traverse questions in tree
        result, total_questions_asked, response, params = node_handle(mode, tree, node, correct_params, total_questions_asked)
        # Alert user and finish if solution is found
        if result:
            if mode == "manual":
                print("Correcting skill with given feedback!")
            corrected = True
            break

    return result, total_questions_asked, response, params


def node_handle(mode, tree, node, correct_params, total_questions_asked):

    if node.score != -1:
        # Generate and print question and ask for response
        query = tree.generate_query(node)
        total_questions_asked += 1

        if mode == "manual":
            print("Question: {}".format(query))
            print("Confidence: {}".format(node.score))

        # If there's only a single parameter force cast to tuple
        if type(node.params) == str:
            cur_params = (node.params, )
        else:
            cur_params = node.params

        # Check if question is correct

        # Manual mode
        if mode == "manual":
            response = str(input("Yes or no? (Y/n)\n"))
            if response.lower() == 'y' or response == "":
                response = True
            else:
                response = False
        else:
            # Automatic mode
            response = set(cur_params).issubset(correct_params)

        # If question was correct, ask constraint question if leaf or
        # recursively ask children if not leaf
        if response:
            if mode == "manual":
                print("Response: Yes")

            if node.leaf:
                # Ask followup question (if exists)
                response = ""
                if node.followup != "":
                    if mode == "manual":
                        # Ask followup question
                        query = node.followup
                        # Substitue instance of parameter type into query
                        for node_param in node.params:
                            for key, value in tree.parameters.items():
                                if node_param in value:
                                    query = query.replace("[{}]".format(key), node_param, 1)
                        print("Followup: {}".format(query))
                        response = input("Give your response:\n")

                return True, total_questions_asked, response, node.params
            else:
                # Iterate through children recursively if needed
                children = tree.get_best_children(node.params)
                if len(children) != 0:
                    for child in children:
                        result, total_questions_asked, response, params = node_handle(mode, tree, child, correct_params, total_questions_asked)
                        if result:
                            return True, total_questions_asked, response, params
                else:
                    print("Couldn't find any viable children nodes!")
        else:
            # If user responds no
            tree.rescore(cur_params)
            if mode == "manual":
                print("Response: No")
            return False, total_questions_asked, "", tuple()

    else:
        return False, total_questions_asked, "", tuple()


if __name__ == "__main__":
    print("Not implemented")
