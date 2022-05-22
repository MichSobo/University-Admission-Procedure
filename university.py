#! python3
"""
University Admission Procedure.
A program that will help to determine the best applicants.
"""
import pandas as pd

# Set departments and scores that are considered in applicants evaluation
DEPARTMENTS = {
    "Mathematics": ["score_math", ],
    "Physics": ["score_physics", "score_math"],
    "Biotech": ["score_chemistry", "score_physics"],
    "Chemistry": ["score_chemistry", ],
    "Engineering": ["score_compscience", "score_math"],
}

# Set limits for the number of accepted applicants
N_ACCEPTED_LIMITS = (2, 10)


def get_n_applicants():
    """Get a valid number of applicants from user input."""
    l_limit, u_limit = N_ACCEPTED_LIMITS
    prompt = '\nNumber of applicants that can be accepted: '

    while True:
        user_input = input(prompt)

        if not user_input.isnumeric():
            print('Input should represent an integer. Try again.')
            continue

        if not (l_limit <= int(user_input) <= u_limit):
            print('Input is out of defined limits. Try again.')
            continue

        return int(user_input)


def get_applicants_from_file(filepath):
    """Get applicants from a text file.

    Reads applicants data from a text file and returns a DataFrame object.

    Args:
        filepath (str): path to the input file;

    Returns:
         pd.DataFrame: DataFrame object with applicants data;
    """
    df = pd.read_csv(
        filepath,
        sep=' ',
        header=None,
        names=['first_name', 'last_name', 'score_physics', 'score_chemistry',
               'score_math', 'score_compscience', 'score_special', 'priority_1',
               'priority_2', 'priority_3'],
        index_col=False
    )

    return df


def get_accepted_applicants(n, df):
    """Get a list of accepted applicant names.

    Returns a dictionary with keys -> departments and values -> DataFrames.
    The latter stores admitted applicants - their names and the final score
    that was taken for candidate evaluation.

    The applicants are sorted by their final score, first name and last name.

    Args:
        n (int): maximum number of accepted applicants;
        df (pd.DataFrame): DataFrame object storing all applicants;

    Returns:
        dict: dictionary with keys -> departments and values -> DataFrames with
            admitted applicants;
    """
    ranking = dict.fromkeys(sorted(DEPARTMENTS.keys()), pd.DataFrame())

    # Loop on every priority
    for priority in ('priority_1', 'priority_2', 'priority_3'):
        # Loop on  every department
        for department, accepted in ranking.items():
            # Check if there can be more applicants admitted
            if len(accepted) < n:
                # Get selection with given priority
                priority_accepted = df[df[priority] == department]

                # Compute equivalent score for given department
                priority_accepted['score_mean'] = \
                    priority_accepted[DEPARTMENTS[department]].mean(axis=1)

                # Set 'score' column with 'score_special' values
                priority_accepted['score'] = priority_accepted['score_special']

                # Get applicants with better 'mean' than 'special' score
                mean_df = priority_accepted[
                    priority_accepted['score_mean'] > priority_accepted['score']]

                # Replace 'score' values with 'score_mean' if needed
                priority_accepted.loc[mean_df.index, 'score'] = mean_df['score_mean']

                # Sort selection based on score, first name and last name
                priority_accepted.sort_values(
                    by=['score', 'first_name', 'last_name'],
                    ascending=[False, True, True],
                    inplace=True
                )

                # Get n applicants to put in accepted dataset
                priority_accepted = priority_accepted[:(n - len(accepted))]
                priority_accepted = priority_accepted[
                    ['first_name', 'last_name', 'score']]

                # Combine selections with existing dataset
                ranking[department] = pd.concat([accepted, priority_accepted])

                # Remove admitted applicants from the original applicant dataset
                df.drop(priority_accepted.index, inplace=True)

    # Sort accepted applicants for every department
    for department, accepted in ranking.items():
        accepted.sort_values(
            by=['score', 'first_name', 'last_name'],
            ascending=[False, True, True],
            inplace=True
        )

    return ranking


def print_accepted_applicants(accepted_applicants):
    """Print a list of accepted applicants for every department."""
    for department, accepted_df in accepted_applicants.items():
        # Print department name
        print(f'\n{department}')

        # Print accepted applicants
        names = accepted_df.iloc[:, 0] + ' ' + accepted_df.iloc[:, 1] +\
            ' ' + accepted_df.iloc[:, 2].astype('str')
        print('\n'.join(names.values))


def save_accepted_applicants(accepted_applicants):
    """Save accepted applicants to file for each department."""
    for department, accepted_df in accepted_applicants.items():
        filename = f'{department.lower()}.txt'
        accepted_df.to_csv(filename, sep=' ', header=False, index=False)


if __name__ == "__main__":
    # Get the maximum number of accepted applicants
    n_max_accepted = get_n_applicants()

    # Get applicants
    applicants_filepath = 'applicants.txt'
    applicants_df = get_applicants_from_file(applicants_filepath)

    # Get accepted applicants
    ranking = get_accepted_applicants(n_max_accepted, applicants_df)

    # Print accepted applicants
    print_accepted_applicants(ranking)

    # Save accepted applicants
    save_accepted_applicants(ranking)
