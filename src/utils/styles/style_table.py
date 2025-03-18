def apply_table_style(table_view):
    """Aplica o estilo à QTableView com hover vibrante e seleção correta da linha inteira."""
    table_view.setStyleSheet("""
        QTableView {
            background-color: #181928;  /* Fundo da tabela */
            color: white;  /* Cor do texto */
            gridline-color: #25283D;  /* Linhas separadoras discretas */
            selection-background-color: #3A57D2;  /* Fundo da linha selecionada (azul vibrante) */
            selection-color: white;
            border: 1px solid #25283D;
            font-size: 14px;
            alternate-background-color: #1F2133; /* Linhas alternadas */
        }

        /* Destaca apenas a linha onde o mouse está passando */
        QTableView::item:hover {
            background-color: #5568E8;  /* Azul mais vibrante ao passar o mouse */
            color: white;
        }

        /* Mantém a linha selecionada destacada mesmo quando o mouse passa sobre ela */
        QTableView::item:selected {
            background-color: #3A57D2;
            color: white;
        }

        QHeaderView::section {
            background-color: #25283D;  /* Cabeçalhos escuros */
            color: white;
            padding: 6px;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #2F324B;
        }

        QTableCornerButton::section {
            background-color: #25283D;
            border: 1px solid #2F324B;
        }
    """)
