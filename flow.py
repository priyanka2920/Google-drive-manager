import pickle

# Path to the token.pickle file
token_path = 'token.pickle'

# Load the token.pickle file
with open(token_path, 'rb') as token_file:
    creds = pickle.load(token_file)

# Print the contents
print("Access Token:", creds.token)
print("Refresh Token:", creds.refresh_token)
print("Token Expiry:", creds.expiry)
print("Client ID:", creds.client_id)
print("Client Secret:", creds.client_secret)


