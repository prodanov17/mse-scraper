# Stage 1: Build the application using Maven
FROM maven:3.8.4-openjdk-17-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the pom.xml file to download the dependencies
COPY pom.xml .

# Download dependencies (to speed up the build process)
RUN mvn dependency:go-offline

# Copy the source code into the container
COPY src /app/src

# Build the application (this will create the JAR file in the target directory)
RUN mvn clean package -DskipTests

# Stage 2: Run the application using Amazon Corretto
FROM amazoncorretto:17

# Set the working directory in the container
WORKDIR /app

# Copy the JAR file from the builder stage
COPY --from=builder /app/target/*.jar /app/application.jar

# Run the application
ENTRYPOINT ["java", "-Xmx2048M", "-jar", "/app/application.jar"]

