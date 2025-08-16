# Use an official Node.js runtime as a parent image
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (if available) to the working directory
COPY package*.json ./

# Install any needed packages
RUN npm install

# Copy the rest of the application's code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8081

# Run the application
CMD ["npm", "run", "web"]
