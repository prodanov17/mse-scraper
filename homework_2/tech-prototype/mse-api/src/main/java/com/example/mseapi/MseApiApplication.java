package com.example.mseapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(exclude = {org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class})
public class MseApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(MseApiApplication.class, args);
    }

}
