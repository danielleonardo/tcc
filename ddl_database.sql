-- public.acordao definition

-- Drop table

-- DROP TABLE public.acordao;

CREATE TABLE public.acordao (
	nome varchar NOT NULL,
	CONSTRAINT acordao_pkey PRIMARY KEY (nome)
);


-- public.ementa definition

-- Drop table

-- DROP TABLE public.ementa;

CREATE TABLE public.ementa (
	nome varchar NOT NULL,
	CONSTRAINT ementa_pkey PRIMARY KEY (nome)
);


-- public.acordao_conteudo definition

-- Drop table

-- DROP TABLE public.acordao_conteudo;

CREATE TABLE public.acordao_conteudo (
	nome_acordao varchar NOT NULL,
	conteudo text NOT NULL,
	CONSTRAINT acordao_conteudo_pk PRIMARY KEY (nome_acordao),
	CONSTRAINT acordao_conteudo_fk FOREIGN KEY (nome_acordao) REFERENCES acordao(nome)
);


-- public.acordao_ementa definition

-- Drop table

-- DROP TABLE public.acordao_ementa;

CREATE TABLE public.acordao_ementa (
	nome_acordao varchar NOT NULL,
	nome_ementa varchar NOT NULL,
	CONSTRAINT pk_acordao_ementa PRIMARY KEY (nome_acordao, nome_ementa),
	CONSTRAINT fk_acordao FOREIGN KEY (nome_acordao) REFERENCES acordao(nome),
	CONSTRAINT fk_ementa FOREIGN KEY (nome_ementa) REFERENCES ementa(nome)
);