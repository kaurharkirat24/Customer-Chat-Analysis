from collections import Counter

def extract_faq(df, n=5):
    questions = [msg for msg in df['message'] if '?' in msg]
    faq_counter = Counter(questions)
    return faq_counter.most_common(n)

def find_common_issues(df, n=5):
    issue_keywords = ['error', 'issue', 'problem', 'help', 'not working', 'fail']
    issues = [msg for msg in df['message'] if any(k in msg.lower() for k in issue_keywords)]
    counter = Counter(issues)
    return counter.most_common(n)
