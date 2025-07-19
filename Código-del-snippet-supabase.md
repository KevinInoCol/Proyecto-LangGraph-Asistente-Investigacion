-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- 1. Crear la tabla para almacenar tus documentos
-- Esta tabla usa los nombres de tu script de Python.
create table documents_langgraph_asistente_de_investigacion (
  id uuid primary key,
  content text,
  metadata jsonb,
  -- El embedding es de 1536 dimensiones porque usas el modelo 'text-embedding-ada-002' de OpenAI
  embedding vector (1536) 
);

-- 2. Crear la función para buscar documentos por similitud
-- Esta función también usa el nombre personalizado de tu script.
create or replace function match_documents_langgraph_asistente_de_investigacion (
  query_embedding vector(1536),
  match_count int,
  filter jsonb
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents_langgraph_asistente_de_investigacion.embedding <=> query_embedding) as similarity
  from documents_langgraph_asistente_de_investigacion
  where metadata @> filter
  order by documents_langgraph_asistente_de_investigacion.embedding <=> query_embedding
  limit match_count;
end;
$$;