-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: fish_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.fish_type AS ENUM (
    'Cory catfish',
    'Guppy',
    'Neon Tetra',
    'Platies'
);


ALTER TYPE public.fish_type OWNER TO postgres;

--
-- Name: sex_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sex_type AS ENUM (
    'M',
    'F'
);


ALTER TYPE public.sex_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: allfish; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.allfish (
    sex public.sex_type NOT NULL,
    date_entered timestamp without time zone NOT NULL,
    id integer NOT NULL,
    age integer,
    type_of_fish public.fish_type
);


ALTER TABLE public.allfish OWNER TO postgres;

--
-- Name: allfish_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.allfish_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.allfish_id_seq OWNER TO postgres;

--
-- Name: allfish_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.allfish_id_seq OWNED BY public.allfish.id;


--
-- Name: fish_feed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fish_feed (
    feed_id integer NOT NULL,
    feed_amount double precision,
    fish_type public.fish_type
);


ALTER TABLE public.fish_feed OWNER TO postgres;

--
-- Name: fish_feed_feed_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fish_feed_feed_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fish_feed_feed_id_seq OWNER TO postgres;

--
-- Name: fish_feed_feed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fish_feed_feed_id_seq OWNED BY public.fish_feed.feed_id;


--
-- Name: allfish id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allfish ALTER COLUMN id SET DEFAULT nextval('public.allfish_id_seq'::regclass);


--
-- Name: fish_feed feed_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fish_feed ALTER COLUMN feed_id SET DEFAULT nextval('public.fish_feed_feed_id_seq'::regclass);


--
-- Data for Name: allfish; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.allfish (sex, date_entered, id, age, type_of_fish) FROM stdin;
M	2024-03-02 13:36:21	8	33	Guppy
F	2024-03-03 12:22:40	9	100	Neon Tetra
\.


--
-- Data for Name: fish_feed; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fish_feed (feed_id, feed_amount, fish_type) FROM stdin;
2	100	Cory catfish
3	150	Guppy
4	200	Neon Tetra
5	250	Platies
\.


--
-- Name: allfish_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.allfish_id_seq', 9, true);


--
-- Name: fish_feed_feed_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fish_feed_feed_id_seq', 5, true);


--
-- Name: allfish allfish_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allfish
    ADD CONSTRAINT allfish_pkey PRIMARY KEY (id);


--
-- Name: fish_feed fish_feed_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fish_feed
    ADD CONSTRAINT fish_feed_pkey PRIMARY KEY (feed_id);


--
-- Name: allfish unique_type_of_fish; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allfish
    ADD CONSTRAINT unique_type_of_fish UNIQUE (type_of_fish);


--
-- PostgreSQL database dump complete
--

