-- ============================================================================
-- SCHEMA DO BANCO DE DADOS - SISTEMA DE VENDAS DESKTOP (SQLITE)
-- ============================================================================
-- Este script define a estrutura relacional do sistema.
-- O comando 'IF NOT EXISTS' previne erros caso a tabela já tenha sido criada.

-- ----------------------------------------------------------------------------
-- 1. TABELA DE USUÁRIOS / FUNCIONÁRIOS
-- Armazena os acessos ao sistema e os perfis de permissão.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    -- ID único do usuário, incrementado automaticamente pelo SQLite
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Nome completo do funcionário (obrigatório)
    nome TEXT NOT NULL,
    
    -- Nome de usuário para login (obrigatório e único no sistema)
    usuario TEXT NOT NULL UNIQUE,
    
    -- Hash da senha gerado via bcrypt (nunca salvar a senha em texto puro!)
    senha_hash TEXT NOT NULL,
    
    -- Cargo/Nível de permissão (restrito apenas a 'Administrador' ou 'Vendedor')
    cargo TEXT NOT NULL CHECK(cargo IN ('Administrador', 'Vendedor')),
    
    -- Status do usuário: 1 = Ativo, 0 = Inativo (soft delete para manter histórico)
    ativo INTEGER NOT NULL DEFAULT 1,
    
    -- Data e hora exatas da criação do registro (gerado automaticamente)
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. TABELA DE PRODUTOS
-- Armazena o catálogo de itens disponíveis para venda e o controle de estoque.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS produtos (
    -- Identificador único interno do produto
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Código de barras do produto (único, ideal para leitura com leitor USB)
    codigo_barras TEXT UNIQUE,
    
    -- Nome/Descrição comercial do produto (obrigatório)
    nome TEXT NOT NULL,
    
    -- Preço pago pelo estabelecimento ao fornecedor (para cálculo de lucro)
    preco_custo REAL NOT NULL DEFAULT 0.0,
    
    -- Preço final cobrado ao cliente
    preco_venda REAL NOT NULL DEFAULT 0.0,
    
    -- Quantidade atual disponível em estoque
    estoque INTEGER NOT NULL DEFAULT 0,
    
    -- Status do produto: 1 = Ativo, 0 = Descontinuado/Inativo
    ativo INTEGER NOT NULL DEFAULT 1,
    
    -- Data de cadastro do produto
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. TABELA DE VENDAS (CABEÇALHO DA VENDA)
-- Registra as transações finalizadas do Ponto de Venda (PDV).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vendas (
    -- Número/Código do cupom de venda
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Data e hora em que a venda foi realizada
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ID do funcionário (vendedor) que realizou a venda
    usuario_id INTEGER NOT NULL,
    
    -- Valor total acumulado da venda
    total REAL NOT NULL DEFAULT 0.0,
    
    -- Método de pagamento utilizado (ex: Dinheiro, Cartão de Crédito, Pix)
    forma_pagamento TEXT NOT NULL DEFAULT 'Dinheiro',
    
    -- CHAVE ESTRANGEIRA: Garante que a venda esteja associada a um usuário válido.
    -- Requer que o PRAGMA foreign_keys = ON esteja ativo no SQLite.
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ----------------------------------------------------------------------------
-- 4. TABELA DE ITENS DA VENDA (DETALHES/CARRINHO)
-- Registra individualmente cada produto vendido em uma determinada venda.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS itens_venda (
    -- Identificador do item da venda
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- ID da venda à qual este item pertence
    venda_id INTEGER NOT NULL,
    
    -- ID do produto comercializado
    produto_id INTEGER NOT NULL,
    
    -- Quantidade de unidades vendidas deste produto específico
    quantidade INTEGER NOT NULL,
    
    -- Preço unitário praticado no momento da venda (histórico de preço)
    preco_unitario REAL NOT NULL,
    
    -- Subtotal calculado: (quantidade * preco_unitario)
    subtotal REAL NOT NULL,
    
    -- CHAVE ESTRANGEIRA 1: Aponta para a venda mãe.
    -- 'ON DELETE CASCADE': Se a venda for cancelada/excluída, os itens são apagados juntos.
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    
    -- CHAVE ESTRANGEIRA 2: Aponta para o produto cadastrado.
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);