create table books(
  isbn varchar not null unique,
  title varchar not null,
  author varchar not null,
  year smallint not null
);
create table userp(
  id Bigserial primary key,
  first_name varchar(150) not null,
  last_name varchar(150) not null,
  email varchar(150) not null unique);

create table userinfo(
  uid bigint references userp(id) unique,
  username varchar(150) not null,
  password varchar(150) not null
);

create table reviews(
  revid bigint references userinfo(uid) not null primary key,
  rating numeric not null,
  reviews varchar null,
  bookid varchar references books(isbn) not null unique

);
