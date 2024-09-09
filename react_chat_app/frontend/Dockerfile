# Use the official Node.js image
FROM node:16

# Set the working directory to /app
WORKDIR /app

# Copy package.json and package-lock.json (if available) to the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code to the working directory in the container
COPY . .

# Build the React app for production
RUN npm run build

# Use an official Nginx image as a parent image
FROM nginx:alpine

# Copy build files to the Nginx container
COPY --from=0 /app/build /usr/share/nginx/html

# Expose the port the app runs on
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
