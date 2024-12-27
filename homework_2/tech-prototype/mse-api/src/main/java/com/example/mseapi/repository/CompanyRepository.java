package com.example.mseapi.repository;

import com.example.mseapi.dto.CompanyDTO;
import com.example.mseapi.model.Company;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;


public interface CompanyRepository extends JpaRepository<Company, String> {
}