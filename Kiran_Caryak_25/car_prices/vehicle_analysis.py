import re
import logging

class VehicleAnalyser:
    x_door_pattern = re.compile(r'\b(\d)dr\b')
    dot_except_with_numbers = re.compile(r'(^|[^\d])\.+([^\d]|$)')

    def similarity_score(self, name1, name2, logger):
        logger.debug(f'Matching the names "{name1}" and "{name2}"')

        def format(name):
            term_mappings = [
                ['speed', 'spd'],
                ['suv', 'sports utility vehicle', 'sports utility'],
                ['continuously variable transmission', 'automatic, cvt', 'cvt'],
                ['diesel', 'biodiesel'],
                ['l',' liters', 'liters', ' liter', 'liter'],
            ]

            def map_terms(name):
                for mapping in term_mappings:
                    for term in mapping[1:]:
                        name = name.replace(term, mapping[0])

                return name

            return self.x_door_pattern.sub(r'\1d', self.dot_except_with_numbers.sub(r'\1 \2', map_terms(name.lower().replace('-', '').replace(',', ' '))))

        def tokenize(name):
            return name.split(' ')

        def filter(tokens):
            filtered_tokens = ['', ' ']
            return (token for token in tokens if token not in filtered_tokens)

        name1_tokens = set(filter(tokenize(format(name1))))
        name2_tokens = set(filter(tokenize(format(name2))))
        logger.debug(f'Resulting tokens:\n{name1_tokens}\n{name2_tokens}')

        return len(name1_tokens.intersection(name2_tokens))
