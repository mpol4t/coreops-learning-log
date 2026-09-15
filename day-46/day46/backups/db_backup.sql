--
-- PostgreSQL database dump
--

\restrict EraSLh5dDrcqkOdUUW3oJ7aEIyYMqRz1B6qJi6gnwuGay4PcMRDnZndFj3GMvp5

-- Dumped from database version 16.15 (Debian 16.15-1.pgdg13+2)
-- Dumped by pg_dump version 16.15 (Debian 16.15-1.pgdg13+2)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assets; Type: TABLE; Schema: public; Owner: coreops
--

CREATE TABLE public.assets (
    id integer NOT NULL,
    hostname text NOT NULL,
    owner_id integer NOT NULL,
    risk integer NOT NULL
);


ALTER TABLE public.assets OWNER TO coreops;

--
-- Name: assets_id_seq; Type: SEQUENCE; Schema: public; Owner: coreops
--

CREATE SEQUENCE public.assets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assets_id_seq OWNER TO coreops;

--
-- Name: assets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coreops
--

ALTER SEQUENCE public.assets_id_seq OWNED BY public.assets.id;


--
-- Name: owners; Type: TABLE; Schema: public; Owner: coreops
--

CREATE TABLE public.owners (
    id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.owners OWNER TO coreops;

--
-- Name: owners_id_seq; Type: SEQUENCE; Schema: public; Owner: coreops
--

CREATE SEQUENCE public.owners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.owners_id_seq OWNER TO coreops;

--
-- Name: owners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coreops
--

ALTER SEQUENCE public.owners_id_seq OWNED BY public.owners.id;


--
-- Name: assets id; Type: DEFAULT; Schema: public; Owner: coreops
--

ALTER TABLE ONLY public.assets ALTER COLUMN id SET DEFAULT nextval('public.assets_id_seq'::regclass);


--
-- Name: owners id; Type: DEFAULT; Schema: public; Owner: coreops
--

ALTER TABLE ONLY public.owners ALTER COLUMN id SET DEFAULT nextval('public.owners_id_seq'::regclass);


--
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: coreops
--

COPY public.assets (id, hostname, owner_id, risk) FROM stdin;
1	blue-web-01	1	20
2	blue-db-01	1	60
3	red-web-01	2	40
\.


--
-- Data for Name: owners; Type: TABLE DATA; Schema: public; Owner: coreops
--

COPY public.owners (id, name) FROM stdin;
1	blue-team
2	red-team
3	empty-team
\.


--
-- Name: assets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coreops
--

SELECT pg_catalog.setval('public.assets_id_seq', 3, true);


--
-- Name: owners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coreops
--

SELECT pg_catalog.setval('public.owners_id_seq', 3, true);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: coreops
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: owners owners_name_key; Type: CONSTRAINT; Schema: public; Owner: coreops
--

ALTER TABLE ONLY public.owners
    ADD CONSTRAINT owners_name_key UNIQUE (name);


--
-- Name: owners owners_pkey; Type: CONSTRAINT; Schema: public; Owner: coreops
--

ALTER TABLE ONLY public.owners
    ADD CONSTRAINT owners_pkey PRIMARY KEY (id);


--
-- Name: assets assets_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coreops
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.owners(id);


--
-- PostgreSQL database dump complete
--

\unrestrict EraSLh5dDrcqkOdUUW3oJ7aEIyYMqRz1B6qJi6gnwuGay4PcMRDnZndFj3GMvp5

