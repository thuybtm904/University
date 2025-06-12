create database univer

create table countries (
	id int IDENTITY(1,1),
	primary key (id),
	name nvarchar(Max)
);

create table universities (
	id int IDENTITY(1,1),
	primary key (id),
	name nvarchar(max),
	short_name nvarchar(max),
	country_id int,
	founded_year int,
	website nvarchar(max),
	description nvarchar(max),
	foreign key (country_id) references countries(id)
);

create table ranking_sources (
	id int IDENTITY(1,1),
	primary key (id),
	name nvarchar(max),
	description nvarchar(max)
);

create table rankings (
	id int IDENTITY(1,1),
	primary key (id),
	university_id int,
	ranking_sources_id int,
	fyear int,
	frank int,
	foreign key (university_id) references universities(id),
	foreign key (ranking_sources_id) references ranking_sources(id)
);

create table programs (
	id int IDENTITY(1,1),
	primary key (id),
	name nvarchar(max),
	level nvarchar(max)
);

create table majors (
	id int IDENTITY(1,1),
	primary key (id),
	name nvarchar(max)
);

create table university_programs (
	id int IDENTITY(1,1),
	primary key (id),
	university_id int,
	program_id int,
	major_id int,
	tuition_fee float,
	duration nvarchar(max),
	foreign key (university_id) references universities(id),
	foreign key (program_id) references programs(id),
	foreign key (major_id) references majors(id)
);

create table criteria (
	id int IDENTITY(1,1),
	primary key (id),
	name nvarchar(max),
	unit nvarchar(max),
	description nvarchar(max)
);

create table university_admission_requirements (
	id int IDENTITY(1,1),
	primary key (id),
	university_id int,
	criteria_id int,
	value nvarchar(max),
	program_id int, 
	foreign key (university_id) references universities(id),
	foreign key (program_id) references programs(id),
	foreign key (criteria_id) references criteria(id)
);