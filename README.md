# Satoshi Quiz Saas - Sats Rewards Quiz Platform
Satoshi Quiz Saas is an innovative service offering an advanced quiz creation platform for businesses. With our service, businesses can generously reward their users with sats (satoshis) - the smallest unit of Bitcoin - for participating in quizzes.

### Main features:

- Quizz Creation: Our easy-to-use platform allows businesses to create interactive and engaging quizzes, customized to their needs and goals.

- Sat Rewards: Users are encouraged to participate in quizzes as they have the opportunity to earn sats based on their performance and score.

- Secure Payment Processing: We use Lndhub as our payment processor, ensuring a secure and fast transaction of sats rewards for users.

- Advanced Access Control: Integrated with Memberstack, our access control system ensures that only authorized users have access to quizzes and rewards.

#### Benefits for Companies:

- User Engagement: Attract and retain users with fun quizzes and sats rewards, which increases customer engagement and loyalty.

- Effective Marketing: Use quizzes as a powerful marketing tool to promote products, services or spread important information.

- Personalized Experience: Customize the quizzes according to the brand identity and establish a stronger connection with the target audience.

- Increased Customer Satisfaction: Provide a rewarding and differentiated experience for users, increasing overall customer satisfaction.

Satoshi Quiz Saas offers a complete solution for businesses that want to leverage the power of quizzes to drive user engagement and reward them with sats. We provide an exciting and innovative way to engage your users, increase brand awareness and achieve meaningful results.

# Setting environment variables
To configure environment variables in your project, you can create an .env file in your project root and define the variables you want to use, in the following format:

```bash
# API Configuration
API_PORT = 80  # The port number for the API.
API_EXTERNAL = "http://localhost:3214"  # The DNS address for the API.

# Firebase Configuration
FIREBASE_CLIENT_ID = ""  # Firebase client ID for authentication.
FIREBASE_PROJECT_ID = ""  # Firebase project ID for database access.
FIREBASE_PRIVATE_KEY = ""  # Firebase private key (ensure to keep it secure).
FIREBASE_CLIENT_EMAIL = ""  # Firebase client email for authentication.
FIREBASE_PRIVATE_KEY_ID = ""  # Firebase private key ID for authentication.
FIREBASE_CLIENT_X509_CERT_URL = ""  # Firebase client X.509 certificate URL for authentication.
```

## Launching the application with Docker.

- Install `docker` and `docker-compose`: Before starting, you must have `docker` and `docker-compose` installed on your machine. You can find installation instructions for both software in the Docker documentation.
- Use the command `docker-compose --env-file .env up -d --remove-orphans` to run the bifrost application easily.
- Use the command `poetry run start` to run application.