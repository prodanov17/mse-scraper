FROM amazoncorretto:17
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} /app/application.jar

CMD apt-get update -y

ENTRYPOINT ["java", "-Xmx2048M", "-jar", "/app/application.jar"]
