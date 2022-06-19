-- migrate:up
create table users (
    id serial primary key,
    name varchar not null
);

-- migrate:down
drop table users;
