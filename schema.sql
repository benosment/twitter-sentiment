drop table if exists tweets;
drop table if exists movies;

create table tweets (
  id integer primary key autoincrement,
  text string not null,
  username string not null,
  sentiment string not null,
  movie_id integer not null,
  FOREIGN KEY (movie_id) references MOVIES
);

create table movies (
  id integer primary key autoincrement,
  title string not null 
);
