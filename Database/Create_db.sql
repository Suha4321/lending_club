DROP TABLE IF EXISTS grade_encode CASCADE;

CREATE TABLE grade_encode
(
   id             bigint    NOT NULL,
   ordinal_score  integer
);
DROP TABLE IF EXISTS grade_enumerate CASCADE;

DROP TABLE IF EXISTS grade_ordinal CASCADE;

CREATE TABLE grade_ordinal
(
   grade          text,
   ordinal_score  integer
);

DROP TABLE IF EXISTS loan_performance CASCADE;

CREATE TABLE loan_performance
(
   id             bigint    NOT NULL,
   issue_year     integer,
   issue_month    integer,
   grade          text,
   loan_amnt      text,
   loan_status    text,
   purpose        text,
   addr_state     text,
   dti            text,
   total_pymnt    text,
   int_rate       text,
   target_status  integer   NOT NULL
);

DROP TABLE IF EXISTS state_encode CASCADE;

CREATE TABLE state_encode
(
   id     bigint   NOT NULL,
   bit_4  text,
   bit_3  text,
   bit_2  text,
   bit_1  text,
   bit_0  text
);
DROP TABLE IF EXISTS state_ordinal CASCADE;

CREATE TABLE state_ordinal
(
   state  text,
   bit_4        text,
   bit_3        text,
   bit_2        text,
   bit_1        text,
   bit_0        text
);
