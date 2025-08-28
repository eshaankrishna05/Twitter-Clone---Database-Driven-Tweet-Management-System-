import getpass
import os
import sqlite3
import sys
import re


# ========================
# Database Setup
# ========================
def get_database_connection():
    if len(sys.argv) < 2:
        print("Error: No database filename provided.")
        sys.exit(1)
    db_filename = sys.argv[1]
    return sqlite3.connect(db_filename)

def Set_Database():
    """
    Create the necessary tables in the SQLite database if they don't already exist.
    """
    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute('''PRAGMA foreign_keys = ON;''')

    # Create tables only if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            usr INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone INTEGER,
            pwd TEXT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS follows (
            flwer INTEGER,
            flwee INTEGER,
            start_date DATE,
            PRIMARY KEY (flwer, flwee),
            FOREIGN KEY (flwer) REFERENCES users(usr) ON DELETE CASCADE,
            FOREIGN KEY (flwee) REFERENCES users(usr) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lists (
            owner_id INTEGER,
            lname TEXT,
            PRIMARY KEY (owner_id, lname),
            FOREIGN KEY (owner_id) REFERENCES users(usr) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS include (
            owner_id INTEGER,
            lname TEXT,
            tid INTEGER,
            PRIMARY KEY (owner_id, lname, tid),
            FOREIGN KEY (owner_id, lname) REFERENCES lists(owner_id, lname) ON DELETE CASCADE,
            FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            tid INTEGER PRIMARY KEY,
            writer_id INTEGER,
            text TEXT,
            tdate DATE,
            ttime TIME,
            replyto_tid INTEGER,
            FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE,
            FOREIGN KEY (replyto_tid) REFERENCES tweets(tid) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS retweets (
            tid INTEGER,
            retweeter_id INTEGER,
            writer_id INTEGER,
            spam INTEGER,
            rdate DATE,
            PRIMARY KEY (tid, retweeter_id),
            FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE,
            FOREIGN KEY (retweeter_id) REFERENCES users(usr) ON DELETE CASCADE,
            FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hashtag_mentions (
            tid INTEGER,
            term TEXT,
            PRIMARY KEY (tid, term),
            FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
        );
    ''')

    conn.commit()
    conn.close()

def masked_input(prompt="Enter your password: "):
    if os.name == 'nt':  # Windows
        import msvcrt
        print(prompt, end='', flush=True)
        password = ''
        while True:
            ch = msvcrt.getch()
            # Handle Enter (carriage return or newline)
            if ch in {b'\r', b'\n'}:
                print('')
                break
            # Handle Backspace
            elif ch == b'\x08':
                if len(password) > 0:
                    password = password[:-1]
                    # Erase last star from display
                    print('\b \b', end='', flush=True)
            # Handle special keys (e.g., function keys, arrow keys)
            elif ch in {b'\x00', b'\xe0'}:
                # Skip the next character which is part of a special key code
                msvcrt.getch()
                continue
            else:
                try:
                    char = ch.decode('utf-8')
                except UnicodeDecodeError:
                    continue
                password += char
                print('*', end='', flush=True)
        return password
    else:  # Linux/macOS: standard getpass (which hides input completely)
        import getpass
        return getpass.getpass(prompt)

# ========================
# Login and Signup
# ========================

def login_screen():
    """
    Display the login screen and handle user choices (login, signup, or exit).
    """
    while True:
        print("\nWelcome to the Twitter Clone!")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            user_id = int(input("Enter your user ID: "))
            password = masked_input("Enter your password: ")
            if login(user_id, password):
                print("Successful login")
                view_followed_tweets(user_id)
                user_menu(user_id)
            else:
                print("Invalid user ID or password.")
        elif choice == '2':
            sign_up()
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")


def login(user_id, password):
    """
    Authenticate a user based on their user ID and password.
    """
    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE usr = ? AND pwd = ?", (user_id, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None
'''
def is_valid_email(email):
    # Check if the email contains '@' and '.'
    return '@' in email and '.' in email
'''
def is_valid_email(email):
    """
    Validate an email address based on standard email rules.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_phone(phone):
    # Check if the phone number contains only numeric characters and meets lenght requirements
    return phone.isdigit() and 7 <= len(phone) <= 15

def sign_up():
    # Ensure the name is not empty
    while True:
        name = input("Enter your name: ").strip()
        if name:
            break
        else:
            print("Error: Name cannot be empty. Please enter a valid name.")

    # Ensure valid email input
    while True:
        email = input("Enter your email: ").strip()
        if is_valid_email(email):
            break
        else:
            print("Error: Invalid email address. Please enter a valid email containing '@' and '.' and meeting basic requirements.")

    # Ensure valid phone number input
    while True:
        phone = input("Enter your phone number: ").strip()
        if is_valid_phone(phone):
            break
        else:
            print("Error: Invalid phone number. Please enter only numeric characters (7 to 15 digits).")

    # Ensure the password is not empty
    while True:
        password = masked_input("Enter your password: ").strip()
        if password:
            break
        else:
            print("Error: Password cannot be empty. Please enter a valid password.")

    # Connect to the database
    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get the maximum user ID and assign a new one
    cursor.execute("SELECT MAX(usr) FROM users")
    max_id = cursor.fetchone()[0]
    new_id = max_id + 1 if max_id else 1

    # Insert the new user into the database
    cursor.execute("INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)",
                   (new_id, name, email, phone, password))
    conn.commit()
    conn.close()

    print(f"Sign up successful! Your user ID is {new_id}.")



# ========================
# User Menu and Functionalities
# ========================

def user_menu(user_id):
    """
    Display the user menu and handle user choices.
    """
    while True:
        print("\nUser Menu")
        print("1. Search for tweets")
        print("2. Search for users")
        print("3. Compose a tweet")
        print("4. List followers")
        print("5. List favorite lists")
        print("6. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            search_tweets(user_id)
        elif choice == '2':
            search_users(user_id)
        elif choice == '3':
            compose_tweet(user_id, replyto_tid=None)
        elif choice == '4':
            list_followers(user_id)
        elif choice == '5':
            list_favorite_lists(user_id)
        elif choice == '6':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

def search_tweets(user_id):
    """
    Search for tweets based on keywords/hashtags with exact or substring matches.
    - Exact hashtags: #party matches #Party (case-insensitive).
    - Keywords: "party" matches text or hashtag substrings (case-insensitive).
    - Explicit "no matches" message.
    """
    keywords = input("Enter keywords (comma-separated): ").strip().split(',')
    keywords = [kw.strip() for kw in keywords if kw.strip()]

    if not keywords:
        print("No valid keywords provided.")
        return

    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query_parts = []
    params = []

    for kw in keywords:
        normalized_kw = kw.lower()
        if kw.startswith("#"):
            # Exact hashtag match (case-insensitive, preserves #)
            query_parts.append("EXISTS (SELECT 1 FROM hashtag_mentions hm WHERE t.tid = hm.tid AND LOWER(hm.term) = LOWER(?))")
            params.append(kw)
        else:
            # Substring in tweet text (case-insensitive)
            query_parts.append("LOWER(t.text) LIKE ?")
            params.append(f"%{normalized_kw}%")
            # Substring in hashtags (case-insensitive)
            query_parts.append("EXISTS (SELECT 1 FROM hashtag_mentions hm WHERE t.tid = hm.tid AND LOWER(hm.term) LIKE ?)")
            params.append(f"%{normalized_kw}%")

    if not query_parts:
        print("No valid search conditions.")
        conn.close()
        return

    final_query = f"""
        SELECT DISTINCT t.tid, t.writer_id, t.tdate, t.ttime, t.text
        FROM tweets t
        WHERE {' OR '.join(query_parts)}
        ORDER BY t.tdate DESC, t.ttime DESC
    """

    cursor.execute(final_query, params)
    results = cursor.fetchall()
    conn.close()

    # Handle no matches explicitly
    if not results:
        print("\nNo tweets found matching the search criteria.")
        return

    # Pagination and display logic
    offset = 0
    page_size = 5

    while offset < len(results):
        print("\n--- Search Results ---")
        print(f"{'tid':<5} | {'writer_id':<10} | {'date':<12} | {'time':<10} | text")
        print("-" * 80)

        batch = results[offset:offset + page_size]
        displayed_tweet_ids = set()

        for tweet in batch:
            print(f"{tweet['tid']:<5} | {tweet['writer_id']:<10} | {tweet['tdate']:<12} | {tweet['ttime']:<10} | {tweet['text']}")
            displayed_tweet_ids.add(tweet['tid'])

        offset += page_size

        while True:
            print("\nOptions:")
            print("Enter a Tweet ID to view details")
            if offset < len(results):
                print("m (more): See more results")
            print("q (quit): Return to menu")

            choice = input("Your choice: ").strip().lower()

            if choice == 'm' and offset < len(results):
                break
            elif choice == 'q':
                return
            elif choice.isdigit():
                tid = int(choice)
                if tid in displayed_tweet_ids:
                    show_tweet_details(user_id, tid)
                else:
                    print("Invalid Tweet ID. Please enter a valid Tweet ID from the displayed list.")
            else:
                print("Invalid input. Please enter a valid Tweet ID, 'm', or 'q'.")

def show_tweet_details(user_id, tid):
    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tweets WHERE replyto_tid = ?", (tid,))
    num_replies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM retweets WHERE tid = ?", (tid,))
    num_retweets = cursor.fetchone()[0]

    print(f"\nTweet {tid} Statistics: {num_replies} replies, {num_retweets} retweets")

    while True:
        print("\nOptions:")
        print("1. Reply to this tweet")
        print("2. Retweet this tweet")
        print("3. Add to favorite list")
        print("4. Go back")

        choice = input("Choose an option: ").strip()
        if choice == '1':
            compose_tweet(user_id, replyto_tid=tid)
        elif choice == '2':
            retweet(user_id, tid)
        elif choice == '3':
            add_to_favorites(user_id, tid)
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

    conn.close()

def retweet(user_id, tid):
    conn = get_database_connection()
    cursor = conn.cursor()

    # Get the original writer_id of the tweet being retweeted
    cursor.execute("SELECT writer_id FROM tweets WHERE tid = ?", (tid,))
    tweet = cursor.fetchone()
    
    if not tweet:
        print("Error: Tweet does not exist.")
        conn.close()
        return

    writer_id = tweet[0]  # Original writer of the tweet

    try:
        # Attempt to insert the retweet (prevents duplicates)
        cursor.execute('''
            INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate)
            VALUES (?, ?, ?, 0, DATE('now'))
        ''', (tid, user_id, writer_id))

        conn.commit()
        print("Tweet successfully retweeted.")

    except sqlite3.IntegrityError:
        print("You have already retweeted this tweet.")

    conn.close()

def add_to_favorites(user_id, tid):
    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch all favorite lists owned by the user
    cursor.execute("SELECT lname FROM lists WHERE owner_id = ?", (user_id,))
    lists = cursor.fetchall()

    if not lists:
        # If no lists exist, display message and exit
        print("You have no favorite lists. Cannot add tweet to favorites.")
        conn.close()
        return

    # If lists exist, user must choose an existing one
    print("\nYour Favorite Lists:")
    for idx, lst in enumerate(lists, start=1):
        print(f"{idx}. {lst[0]}")

    while True:
        try:
            list_choice = int(input("Select a list number to add this tweet to: ").strip())
            if 1 <= list_choice <= len(lists):
                selected_list = lists[list_choice - 1][0]
                break
            else:
                print("Invalid choice. Please enter a valid list number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Insert the tweet into the selected favorite list
    try:
        cursor.execute('''
            INSERT INTO include (owner_id, lname, tid)
            VALUES (?, ?, ?)
        ''', (user_id, selected_list, tid))
        conn.commit()
        print(f"Tweet added to '{selected_list}'.")
    except sqlite3.IntegrityError:
        print(f"Tweet is already in '{selected_list}'.")
    finally:
        conn.close()

def search_users(current_user_id):
    
    """
    Search for users by name, display paginated results, and allow viewing detailed information.
    """
    keyword = input("Enter a keyword to search for users: ").strip()
    if not keyword:
        print("Keyword cannot be empty.")
        return

    conn = get_database_connection()
    cursor = conn.cursor()

    # Case-insensitive search for users with names containing the keyword
    cursor.execute('''
        SELECT usr, name 
        FROM users 
        WHERE name LIKE ? COLLATE NOCASE 
        ORDER BY LENGTH(name) ASC, name ASC
    ''', ('%' + keyword + '%',))
    
    all_users = cursor.fetchall()
    conn.close()

    if not all_users:
        print("No users found.")
        return

    offset = 0
    limit = 5
    while True:
        current_page = all_users[offset:offset + limit]
        print("\nSearch Results:")
        for user in current_page:
            print(f"User ID: {user[0]}, Name: {user[1]}")

        user_ids = [str(user[0]) for user in current_page]
        print("\nOptions:")
        print("Enter a User ID to view details")
        if len(all_users) > offset + limit:
            print("m (more): See more results")
        print("q (quit): Return to the menu")

        choice = input("Your choice: ").strip().lower()

        if choice == 'm' and len(all_users) > offset + limit:
            offset += limit
        elif choice == 'q':
            return
        elif choice in user_ids:
            selected_user_id = int(choice)
            display_user_details(selected_user_id, current_user_id)
        else:
            print("Invalid input. Please enter a valid User ID, 'm', or 'q'.")

def display_user_details(selected_user_id, current_user_id):
    """
    Display detailed information about a user, including tweets and follow options.
    """
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM users WHERE usr = ?", (selected_user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            print("User not found.")
            return
        user_name = user_row[0]

        # Get user statistics
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer_id = ?", (selected_user_id,))
        num_tweets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (selected_user_id,))
        num_following = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (selected_user_id,))
        num_followers = cursor.fetchone()[0]

        # Get recent tweets
        cursor.execute('''
            SELECT text, tdate, ttime 
            FROM tweets 
            WHERE writer_id = ? 
            ORDER BY tdate DESC, ttime DESC 
            LIMIT 3
        ''', (selected_user_id,))
        recent_tweets = cursor.fetchall()

        print(f"\nUser Details - {user_name} (ID: {selected_user_id})")
        print(f"Number of Tweets: {num_tweets}")
        print(f"Following: {num_following}")
        print(f"Followers: {num_followers}")
        print("\nRecent Tweets:")
        if recent_tweets:
            for tweet in recent_tweets:
                print(f"- {tweet[0]} (Date: {tweet[1]}, Time: {tweet[2]})")
        else:
            print("No recent tweets.")

        # Check if current user is already following the selected user
        cursor.execute("SELECT 1 FROM follows WHERE flwer = ? AND flwee = ?", 
                      (current_user_id, selected_user_id))
        is_following = cursor.fetchone() is not None

        while True:
            print("\nOptions:")
            if ((not is_following) and (selected_user_id != current_user_id)):
                print("1. Follow this user")
            else:
                print("You are already following this user.")
            print("2. View all tweets")
            print("3. Return to search results")
            option = input("Enter your choice: ").strip()

            if option == '1' and not is_following and selected_user_id != current_user_id:
                try:
                    cursor.execute('''
                        INSERT INTO follows (flwer, flwee, start_date)
                        VALUES (?, ?, DATE('now'))
                    ''', (current_user_id, selected_user_id))
                    conn.commit()
                    print("You are now following this user.")
                    is_following = True
                except sqlite3.IntegrityError:
                    print("You are already following this user.")
                    is_following = True
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif option == '2':
                cursor.execute('''
                    SELECT text, tdate, ttime 
                    FROM tweets 
                    WHERE writer_id = ? 
                    ORDER BY tdate DESC, ttime DESC
                ''', (selected_user_id,))
                all_tweets = cursor.fetchall()
                print("\nAll Tweets:")
                if all_tweets:
                    for tweet in all_tweets:
                        print(f"- {tweet[0]} (Date: {tweet[1]}, Time: {tweet[2]})")
                else:
                    print("No tweets available.")
            elif option == '3':
                break
            else:
                print("Invalid option. Please try again.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
        

def compose_tweet(user_id, replyto_tid):
    """
    Allow a user to compose and post a tweet.
    Supports:
    - Regular tweets (no replyto_tid passed).
    - Reply tweets (replyto_tid is passed when replying to another tweet).
    - Ensures no duplicate hashtags in the tweet.
    """
    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    text = input("Enter your tweet: ").strip()
    if not text:
        print("Tweet cannot be empty.")
        conn.close()
        return

    # Extract hashtags from the text
    hashtags = re.findall(r"#\w+", text)

    # Convert to lowercase for case-insensitive duplicate check
    lower_hashtags = [h.lower() for h in hashtags]

    # Check for duplicate hashtags (case insensitive)
    if len(lower_hashtags) != len(set(lower_hashtags)):
        print("Tweet rejected: Duplicate hashtags are not allowed.")
        conn.close()
        return

    # Get new Tweet ID
    cursor.execute("SELECT MAX(tid) FROM tweets")
    max_tid = cursor.fetchone()[0]
    new_tid = (max_tid or 0) + 1

    # Insert into `tweets` table - handles both normal and reply tweets
    if replyto_tid is None:
        cursor.execute('''
            INSERT INTO tweets (tid, writer_id, text, tdate, ttime)
            VALUES (?, ?, ?, DATE('now'), TIME('now'))
        ''', (new_tid, user_id, text))
    else:
        cursor.execute('''
            INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
            VALUES (?, ?, ?, DATE('now'), TIME('now'), ?)
        ''', (new_tid, user_id, text, replyto_tid))

    # Insert hashtags into `hashtag_mentions` table
    for hashtag in hashtags:
        cursor.execute('''
            INSERT INTO hashtag_mentions (tid, term)
            VALUES (?, ?)
        ''', (new_tid, hashtag))

    conn.commit()
    conn.close()

    print("Tweet posted successfully!")
    if hashtags:
        print(f"Hashtags saved: {', '.join(hashtags)}")

def list_followers(user_id):
    """
    List all followers of the logged-in user in a tabular format.
    Paginate if there are more than 5 followers.
    """

    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all followers of the logged-in user
    cursor.execute('''
        SELECT u.usr, u.name 
        FROM follows f
        JOIN users u ON f.flwer = u.usr
        WHERE f.flwee = ?
        ORDER BY u.name ASC
    ''', (user_id,))

    followers = cursor.fetchall()
    conn.close()

    if not followers:
        print("You have no followers.")
        return

    offset = 0
    limit = 5

    while True:
        print("\nFollowers List")
        print(f"{'User ID':<10} | {'Name':<20}")
        print("-" * 32)

        for follower in followers[offset:offset + limit]:
            print(f"{follower['usr']:<10} | {follower['name']:<20}")

        print("\nOptions:")
        print("Enter a User ID to view more details about a follower")
        if len(followers) > offset + limit:
            print("m (more): See more results")
        print("q (quit): Return to the menu")

        choice = input("Your choice: ").strip().lower()

        if choice == 'm' and len(followers) > offset + limit:
            offset += limit
        elif choice == 'q':
            break
        elif choice.isdigit():
            selected_user_id = int(choice)
            if any(f['usr'] == selected_user_id for f in followers):
                display_follower_details(user_id, selected_user_id)
            else:
                print("Invalid User ID. Please enter a valid User ID from the list.")
        else:
            print("Invalid input. Please enter a valid User ID, 'm', or 'q'.")

def display_follower_details(current_user_id, follower_id):
    """
    Display detailed information about a follower.
    Allow following the user if not already followed, or viewing all tweets.
    """

    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch follower's basic information
    cursor.execute("SELECT name FROM users WHERE usr = ?", (follower_id,))
    follower = cursor.fetchone()

    if not follower:
        print("User not found.")
        conn.close()
        return

    name = follower['name']

    # Fetch stats: number of tweets, following count, follower count
    cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer_id = ?", (follower_id,))
    tweet_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (follower_id,))
    following_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (follower_id,))
    follower_count = cursor.fetchone()[0]

    # Fetch up to 3 most recent tweets
    cursor.execute('''
        SELECT text, tdate, ttime
        FROM tweets
        WHERE writer_id = ?
        ORDER BY tdate DESC, ttime DESC
        LIMIT 3
    ''', (follower_id,))
    recent_tweets = cursor.fetchall()

    print(f"\nFollower Details - {name} (User ID: {follower_id})")
    print(f"Number of Tweets: {tweet_count}")
    print(f"Following: {following_count}")
    print(f"Followers: {follower_count}")

    print("\nRecent Tweets:")
    if recent_tweets:
        for tweet in recent_tweets:
            print(f"- {tweet['text']} (Date: {tweet['tdate']}, Time: {tweet['ttime']})")
    else:
        print("No recent tweets.")

    # Check if the logged-in user is already following this follower
    cursor.execute("SELECT 1 FROM follows WHERE flwer = ? AND flwee = ?", (current_user_id, follower_id))
    already_following = cursor.fetchone() is not None

    while True:
        print("\nOptions:")
        if not already_following and current_user_id != follower_id:
            print("1. Follow this user")
        else:
            print("You are already following this user.")
        print("2. View all tweets")
        print("3. Return to followers list")

        option = input("Enter your choice: ").strip()

        if option == '1' and not already_following and current_user_id != follower_id:
            try:
                cursor.execute('''
                    INSERT INTO follows (flwer, flwee, start_date)
                    VALUES (?, ?, DATE('now'))
                ''', (current_user_id, follower_id))
                conn.commit()
                print(f"You are now following {name}.")
                already_following = True
            except sqlite3.IntegrityError:
                print("You are already following this user.")
            except Exception as e:
                print(f"Error: {e}")

        elif option == '2':
            view_all_tweets(follower_id)
        elif option == '3':
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()


def view_all_tweets(user_id):
    """
    Display all tweets written by a specific user.
    """

    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT text, tdate, ttime
        FROM tweets
        WHERE writer_id = ?
        ORDER BY tdate DESC, ttime DESC
    ''', (user_id,))

    tweets = cursor.fetchall()

    if not tweets:
        print("This user has no tweets.")
    else:
        print("\nAll Tweets:")
        for tweet in tweets:
            print(f"- {tweet['text']} (Date: {tweet['tdate']}, Time: {tweet['ttime']})")

    conn.close()



def list_favorite_lists(user_id):
    """
    List all favorite lists of the logged-in user, along with the TIDs stored in each list.
    """
    conn = get_database_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query to get all lists belonging to the user
    cursor.execute('''
        SELECT lname 
        FROM lists 
        WHERE owner_id = ?
    ''', (user_id,))

    lists = cursor.fetchall()

    if not lists:
        print("You have no favorite lists.")
        conn.close()
        return

    # For each list, get the TIDs stored in it
    for list_row in lists:
        list_name = list_row["lname"]

        cursor.execute('''
            SELECT tid 
            FROM include 
            WHERE owner_id = ? AND lname = ?
        ''', (user_id, list_name))

        tids = cursor.fetchall()

        tids_str = ', '.join(str(row["tid"]) for row in tids) if tids else "No tweets in this list"
        print(f"{list_name}: {tids_str}")

    conn.close()

def view_followed_tweets(user_id, offset=0, limit=5):
    """
    Display tweets and retweets from users followed by the logged-in user in a tabular format.
    """
    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch total count for followed tweets and retweets
    cursor.execute('''
        SELECT COUNT(*) FROM (
            SELECT tid FROM tweets WHERE writer_id IN (SELECT flwee FROM follows WHERE flwer = ?)
            UNION ALL
            SELECT tid FROM retweets WHERE retweeter_id IN (SELECT flwee FROM follows WHERE flwer = ?) AND spam = 0
        )
    ''', (user_id, user_id))
    total_count = cursor.fetchone()[0]

    # Fetch actual tweets/retweets for the current page
    cursor.execute('''
        SELECT 'tweet' AS type, tid, tdate, ttime, 0 as spam
        FROM tweets
        WHERE writer_id IN (SELECT flwee FROM follows WHERE flwer = ?)
        UNION ALL
        SELECT 'retweet' AS type, tid, rdate AS tdate, NULL AS ttime, spam
        FROM retweets
        WHERE retweeter_id IN (SELECT flwee FROM follows WHERE flwer = ?) AND spam = 0
        ORDER BY tdate DESC, ttime DESC
        LIMIT ? OFFSET ?
    ''', (user_id, user_id, limit, offset))

    tweets = cursor.fetchall()
    conn.close()

    if not tweets:
        print("No tweets or retweets to display.")
        return

    # Print header
    print(f"{'Type':<10} | {'Tweet ID':<10} | {'Date':<12} | {'Time':<8} | {'Spam'}")
    print("-" * 50)

    # Print tweets
    for tweet in tweets:
        print(f"{tweet[0]:<10} | {tweet[1]:<10} | {tweet[2]:<12} | {tweet[3] or 'N/A':<8} | {tweet[4]}")

    if offset + len(tweets) < total_count:
        more = input("Show more tweets? (y/n): ").strip().lower()
        if more == 'y':
            view_followed_tweets(user_id, offset + limit, limit)

            
# ========================
# Main Program
# ========================

if __name__ == "__main__":
    # Create tables if they don't exist
    Set_Database()
    
    # Start the login screen
    login_screen()
