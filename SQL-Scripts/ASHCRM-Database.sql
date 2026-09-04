CREATE DATABASE ashcrm;

CREATE TABLE student (
	student_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	section VARCHAR(50) NOT NULL,
	address VARCHAR(255) NOT NULL,
	date_of_birth DATE NOT NULL,
	religion VARCHAR(50) NOT NULL,
	nationality VARCHAR(50) NOT NULL,
	emergency_contact_number VARCHAR(20) NOT NULL,
	family_history JSON NOT NULL,
	medical_history JSON NOT NULL,
	immunizations JSON NOT NULL,
	psychosocial_history JSON NOT NULL,
	sexual_history JSON NOT NULL
);

CREATE TABLE staff (
	staff_id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	position VARCHAR(50) NOT NULL,
	email VARCHAR(100) NOT NULL,
	contact_number VARCHAR(20)
);

CREATE TABLE clinic_visit (
	visit_id INT AUTO_INCREMENT PRIMARY KEY,
	student_id INT NOT NULL,
	FOREIGN KEY (student_id) REFERENCES student(student_id),
    date DATE NOT NULL,
	time_in TIME NOT NULL,
	time_out TIME NOT NULL,
	chief_complaints TEXT NOT NULL,
	treatment TEXT
);

CREATE TABLE incident (
	incident_id INT AUTO_INCREMENT PRIMARY KEY,
	student_id INT NOT NULL,
	FOREIGN KEY (student_id) REFERENCES student(student_id),
	date DATE NOT NULL,
	time TIME NOT NULL,
	description TEXT NOT NULL,
	treatment TEXT
);

CREATE TABLE medical_service_form (
	service_form_id INT AUTO_INCREMENT PRIMARY KEY,
	student_id INT NOT NULL,
	FOREIGN KEY (student_id) REFERENCES student(student_id),
	staff_id INT NOT NULL,
	FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
	time_start TIME NOT NULL,
	time_end TIME NOT NULL,
	date DATE NOT NULL,
	purpose TEXT NOT NULL
);

CREATE TABLE medical_certificates (
	certificate_id INT AUTO_INCREMENT PRIMARY KEY,
	student_id INT NOT NULL,
	FOREIGN KEY (student_id) REFERENCES student(student_id),
	staff_id INT NOT NULL,
	FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
	date_approved DATE NOT NULL,
	event_name VARCHAR(100) NOT NULL
);

CREATE TABLE medical_supplies (
	medical_item_id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	quantity INT NOT NULL
);

CREATE TABLE medical_equipment (
	equipment_id INT AUTO_INCREMENT PRIMARY KEY,
	type VARCHAR(100) NOT NULL
);

CREATE TABLE borrowed_items (
	items_id INT AUTO_INCREMENT PRIMARY KEY,
	borrow_log_id INT NOT NULL,
	FOREIGN KEY (borrow_log_id) REFERENCES medical_service_form(service_form_id),
	equipment_id INT NOT NULL,
	FOREIGN KEY (equipment_id) REFERENCES medical_equipment(equipment_id)
);

CREATE TABLE medical_supplies_used_clinic_visit (
	visit_supplies_id INT AUTO_INCREMENT PRIMARY KEY,
	medical_item_id INT NOT NULL,
	FOREIGN KEY (medical_item_id) REFERENCES medical_supplies(medical_item_id),
	visit_id INT NOT NULL,
	FOREIGN KEY (visit_id) REFERENCES clinic_visit(visit_id),
	quantity INT NOT NULL
);

CREATE TABLE medical_supplies_used_incidents (
	incident_supplies_id INT AUTO_INCREMENT PRIMARY KEY,
	medical_item_id INT NOT NULL,
	FOREIGN KEY (medical_item_id) REFERENCES medical_supplies(medical_item_id),
	incident_id INT NOT NULL,
	FOREIGN KEY (incident_id) REFERENCES incident(incident_id),
	quantity INT NOT NULL
);

CREATE TABLE medical_supplies_used_service_form (
	service_supplies_id INT AUTO_INCREMENT PRIMARY KEY,
	medical_item_id INT NOT NULL,
	FOREIGN KEY (medical_item_id) REFERENCES medical_supplies(medical_item_id),
	service_form_id INT NOT NULL,
	FOREIGN KEY (service_form_id) REFERENCES medical_service_form(service_form_id),
	quantity INT NOT NULL
);

CREATE TABLE involved_staff_clinic_visit (
	visit_staff_id INT AUTO_INCREMENT PRIMARY KEY,
	visit_id INT NOT NULL,
	FOREIGN KEY (visit_id) REFERENCES clinic_visit(visit_id),
	staff_id INT NOT NULL,
	FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

CREATE TABLE involved_staff_incidents (
	incident_staff_id INT AUTO_INCREMENT PRIMARY KEY,
	incident_id INT NOT NULL,
	FOREIGN KEY (incident_id) REFERENCES incident(incident_id),
	staff_id INT NOT NULL,
	FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

CREATE TABLE involved_staff_medical_service_form (
	service_form_staff_id INT AUTO_INCREMENT PRIMARY KEY,
	service_form_id INT NOT NULL,
	FOREIGN KEY (service_form_id) REFERENCES medical_service_form(service_form_id),
	staff_id INT NOT NULL,
	FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);