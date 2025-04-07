import sys
import os
import numpy as np
import pandas as pd
import webbrowser
import tempfile
import io
import qrcode
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QCheckBox, QGroupBox, 
                            QGridLayout, QDoubleSpinBox, QSpinBox, QTabWidget, QSplitter,
							QMessageBox, QDialog, QFrame, QToolBar, QSizePolicy)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from PyQt5.QtCore import QLocale, Qt, QRect, QSize
import plotly.graph_objects as go
import plotly.io as pio

# Definir paleta de cores para um tema elegante
COLORS = {
    'background': '#f9f9f9',
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'accent': '#3498db',
    'text': '#2c3e50',
    'graph1': '#3498db',
    'graph2': '#2ecc71',
    'graph3': '#e74c3c',
    'graph4': '#9b59b6',
}

class DividendPortfolioCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dividend Portfolio Calculator")
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        
        # Remover barra de título padrão
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Create modern toolbar para agir como barra de título personalizada
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setMovable(False)
        
        # Remover margens e bordas da toolbar
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {COLORS['accent']};
                border: none;
                spacing: 0px;
                padding: 0px;
                margin: 0px;
            }}
        """)
        
        self.addToolBar(toolbar)
        
        # Criar título e botões de controle em um widget
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)
        title_widget.setStyleSheet(f"background-color: {COLORS['accent']}; margin: 0px; padding: 0px; border: none;")
        
        # Título da aplicação
        title_label = QLabel("Dividend Portfolio Calculator")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: white;
            background-color: transparent;
            margin: 0px;
            padding: 8px;
        """)
        
        # Adicionar botões de controle
        btn_minimize = QPushButton("−")
        btn_maximize = QPushButton("⧠")
        btn_close = QPushButton("×")
        
        # Estilizar botões
        control_btn_style = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 4px 8px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """
        
        btn_minimize.setStyleSheet(control_btn_style)
        btn_maximize.setStyleSheet(control_btn_style)
        btn_close.setStyleSheet(control_btn_style + "QPushButton:hover { background-color: rgba(255, 0, 0, 0.6); }")
        
        # Conectar botões às ações da janela
        btn_minimize.clicked.connect(self.showMinimized)
        btn_maximize.clicked.connect(self.toggle_maximize)
        btn_close.clicked.connect(self.close)
        
        # Adicionar widgets ao layout do título
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(btn_minimize)
        title_layout.addWidget(btn_maximize)
        title_layout.addWidget(btn_close)
        
        # Adicionar widget de título à toolbar, garantindo que ocupe todo o espaço
        toolbar.addWidget(title_widget)
        title_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Permitir arrastar a janela a partir da toolbar
        title_widget.mousePressEvent = self.mousePressEvent
        title_widget.mouseMoveEvent = self.mouseMoveEvent
        title_label.mousePressEvent = self.mousePressEvent
        title_label.mouseMoveEvent = self.mouseMoveEvent
        
        # Criar pasta para salvar os gráficos (na área de trabalho ou no diretório atual)
        self.desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.graphs_folder = os.path.join(self.desktop_path, 'DividendGraphs')
        
        if not os.path.exists(self.graphs_folder):
            try:
                os.makedirs(self.graphs_folder)
            except:
                # Se não conseguir criar na área de trabalho, usar o diretório atual
                self.graphs_folder = 'DividendGraphs'
                if not os.path.exists(self.graphs_folder):
                    os.makedirs(self.graphs_folder)
        
        # Definir caminhos dos arquivos
        self.html_files = {
            'portfolio': os.path.join(self.graphs_folder, 'portfolio_balance.html'),
            'dividend': os.path.join(self.graphs_folder, 'dividend_income.html'),
            'yield': os.path.join(self.graphs_folder, 'yield_on_cost.html')
        }
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Área de entrada
        input_group = QGroupBox("Input Parameters")
        input_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {COLORS['accent']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLORS['primary']};
            }}
        """)
        
        input_layout = QGridLayout()
        input_layout.setVerticalSpacing(6)  # Reduzir espaçamento vertical
        input_layout.setContentsMargins(10, 10, 10, 10)  # Reduzir margens
        
        # Definir área de entrada
        row = 0
        
        # Capital inicial
        input_layout.addWidget(QLabel("Starting Principal ($):"), row, 0)
        self.starting_principal = QDoubleSpinBox()
        self.starting_principal.setRange(0, 10000000)
        self.starting_principal.setDecimals(2)
        self.starting_principal.setSingleStep(1000)
        self.starting_principal.setValue(10000)
        self.starting_principal.setLocale(QLocale('en_US'))
        self.starting_principal.setStyleSheet(self.get_input_style())
        input_layout.addWidget(self.starting_principal, row, 1)
        row += 1
        
        # Rendimento anual de dividendos
        input_layout.addWidget(QLabel("Annual Dividend Yield (%):"), row, 0)
        self.annual_dividend_yield = QDoubleSpinBox()
        self.annual_dividend_yield.setRange(0, 100)
        self.annual_dividend_yield.setDecimals(2)
        self.annual_dividend_yield.setSingleStep(0.1)
        self.annual_dividend_yield.setValue(4.0)
        self.annual_dividend_yield.setLocale(QLocale('en_US'))
        self.annual_dividend_yield.setStyleSheet(self.get_input_style())
        input_layout.addWidget(self.annual_dividend_yield, row, 1)
        row += 1
        
        # Encontre a seção atual que define o container de taxa
        input_layout.addWidget(QLabel("Dividend Tax Rate (%):"), row, 0)
        
        # Modifique o layout do container de taxa para ser mais compacto
        tax_container = QWidget()
        tax_layout = QHBoxLayout(tax_container)
        tax_layout.setContentsMargins(0, 0, 0, 0)
        tax_layout.setSpacing(2)  # Espaçamento ainda menor
        
        # Altere a checkbox para usar menos espaço
        self.is_taxed = QCheckBox("Is Taxed?")
        self.is_taxed.setChecked(True)
        self.is_taxed.setStyleSheet("""
            QCheckBox {
                padding-right: 0px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
        """)
        self.is_taxed.stateChanged.connect(self.toggle_tax_rate)
        tax_layout.addWidget(self.is_taxed)
        
        # Defina o tamanho máximo para o spinbox de taxa
        self.dividend_tax_rate = QDoubleSpinBox()
        self.dividend_tax_rate.setRange(0, 100)
        self.dividend_tax_rate.setDecimals(2)
        self.dividend_tax_rate.setSingleStep(0.5)
        self.dividend_tax_rate.setValue(30)
        self.dividend_tax_rate.setLocale(QLocale('en_US'))
        self.dividend_tax_rate.setStyleSheet(self.get_input_style())
        self.dividend_tax_rate.setFixedWidth(80)  # Definir largura fixa menor
        self.dividend_tax_rate.setEnabled(False)
        tax_layout.addWidget(self.dividend_tax_rate)
        tax_layout.addStretch()  # Adicionar espaçador para alinhar à esquerda
        
        # Adicione o container ao layout principal
        input_layout.addWidget(tax_container, row, 1)
        row += 1
        
        # Aumento anual esperado de dividendos
        input_layout.addWidget(QLabel("Expected Annual Dividend Increase (%):"), row, 0)
        self.expected_annual_dividend_increase = QDoubleSpinBox()
        self.expected_annual_dividend_increase.setRange(0, 100)
        self.expected_annual_dividend_increase.setDecimals(2)
        self.expected_annual_dividend_increase.setSingleStep(0.5)
        self.expected_annual_dividend_increase.setValue(3)
        self.expected_annual_dividend_increase.setLocale(QLocale('en_US'))
        self.expected_annual_dividend_increase.setStyleSheet(self.get_input_style())
        input_layout.addWidget(self.expected_annual_dividend_increase, row, 1)
        row += 1
        
        # Frequência de pagamento de dividendos
        input_layout.addWidget(QLabel("Dividend Payment Frequency:"), row, 0)
        self.dividend_payment_frequency = QComboBox()
        self.dividend_payment_frequency.addItems(["Monthly", "Quarterly", "Yearly"])
        self.dividend_payment_frequency.setCurrentIndex(1)  # Trimestral como padrão
        self.dividend_payment_frequency.setStyleSheet(self.get_input_style())
        input_layout.addWidget(self.dividend_payment_frequency, row, 1)
        row += 1
        
        # Tipo de contribuição
        input_layout.addWidget(QLabel("Contribution Type:"), row, 0)
        self.contribution_type = QComboBox()
        self.contribution_type.addItems(["Monthly Contribution", "Annual Contribution"])
        self.contribution_type.setCurrentIndex(0)  # Mensal como padrão
        self.contribution_type.setStyleSheet(self.get_input_style())
        self.contribution_type.currentIndexChanged.connect(self.update_contribution_label)
        input_layout.addWidget(self.contribution_type, row, 1)
        row += 1
        
        # Valor da contribuição
        self.contribution_label = QLabel("Monthly Contribution ($):")
        input_layout.addWidget(self.contribution_label, row, 0)
        self.periodic_contribution = QDoubleSpinBox()
        self.periodic_contribution.setRange(0, 1000000)
        self.periodic_contribution.setDecimals(2)
        self.periodic_contribution.setSingleStep(100)
        self.periodic_contribution.setValue(0)
        self.periodic_contribution.setLocale(QLocale('en_US'))
        self.periodic_contribution.setStyleSheet(self.get_input_style())
        input_layout.addWidget(self.periodic_contribution, row, 1)
        row += 1
        
        # Anos investidos
        input_layout.addWidget(QLabel("Years Invested:"), row, 0)
        self.years_invested = QSpinBox()
        self.years_invested.setRange(1, 50)
        self.years_invested.setValue(10)
        self.years_invested.setStyleSheet(self.get_input_style())
        input_layout.addWidget(self.years_invested, row, 1)
        row += 1
        
        # Reinvestimento de dividendos
        input_layout.addWidget(QLabel("Reinvest Dividends:"), row, 0)
        self.dividend_reinvestment = QCheckBox()
        self.dividend_reinvestment.setChecked(True)
        self.dividend_reinvestment.setStyleSheet("""
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        input_layout.addWidget(self.dividend_reinvestment, row, 1)
        row += 1
        
        # Valorização anual esperada das ações
        input_layout.addWidget(QLabel("Expected Annual Share Price Appreciation (%):"), row, 0)
        self.expected_annual_share_price_appreciation = QDoubleSpinBox()
        self.expected_annual_share_price_appreciation.setRange(-20, 100)
        self.expected_annual_share_price_appreciation.setDecimals(2)
        self.expected_annual_share_price_appreciation.setSingleStep(0.5)
        self.expected_annual_share_price_appreciation.setValue(3)
        self.expected_annual_share_price_appreciation.setLocale(QLocale('en_US'))
        self.expected_annual_share_price_appreciation.setStyleSheet(self.get_input_style())
        input_layout.addWidget(self.expected_annual_share_price_appreciation, row, 1)
        row += 1
        
        # Botão de cálculo
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #1f6aa5;
            }}
        """)
        self.calculate_button.clicked.connect(self.calculate_and_plot)
        input_layout.addWidget(self.calculate_button, row, 0, 1, 2)
        row += 1
        
        input_group.setLayout(input_layout)
        
        # Configure a área de resultados com botões para os diferentes gráficos
        results_group = QGroupBox("Results")
        results_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {COLORS['accent']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLORS['primary']};
            }}
        """)
        
        results_layout = QVBoxLayout()
        
        # Criar botões para os gráficos
        button_style = f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;  /* Reduzir padding */
                font-weight: bold;
                margin: 5px;  /* Reduzir margem */
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #1f6aa5;
            }}
        """
        
        self.portfolio_balance_button = QPushButton("View Portfolio Balance Chart")
        self.portfolio_balance_button.setStyleSheet(button_style)
        self.portfolio_balance_button.clicked.connect(lambda: self.view_chart('portfolio'))
        results_layout.addWidget(self.portfolio_balance_button)
        
        self.dividend_income_button = QPushButton("View Dividend Income Chart")
        self.dividend_income_button.setStyleSheet(button_style)
        self.dividend_income_button.clicked.connect(lambda: self.view_chart('dividend'))
        results_layout.addWidget(self.dividend_income_button)
        
        self.yield_on_cost_button = QPushButton("View Yield on Cost Chart")
        self.yield_on_cost_button.setStyleSheet(button_style)
        self.yield_on_cost_button.clicked.connect(lambda: self.view_chart('yield'))
        results_layout.addWidget(self.yield_on_cost_button)
        
        results_layout.addStretch()
        results_group.setLayout(results_layout)
        
        self.results_table_button = QPushButton("View Results Table")
        self.results_table_button.setStyleSheet(button_style)
        self.results_table_button.clicked.connect(self.view_results_table)
        results_layout.addWidget(self.results_table_button)
        
        # Adicionar linha divisória
        results_layout.addSpacing(15)
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet(f"background-color: {COLORS['accent']}; max-height: 1px;")
        results_layout.addWidget(divider)
        results_layout.addSpacing(15)
        
        # Botão de doação
        self.donate_button = QPushButton("Support This Project")
        self.donate_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #F7931A;  /* Bitcoin orange */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                margin: 5px;
            }}
            QPushButton:hover {{
                background-color: #E87B18;
            }}
            QPushButton:pressed {{
                background-color: #D67016;
            }}
        """)
        self.donate_button.clicked.connect(self.show_donate_dialog)
        results_layout.addWidget(self.donate_button)
        
        # Adicionar widgets ao layout principal
        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(QVBoxLayout())
        left_widget.layout().addWidget(input_group)
        
        right_widget = QWidget()
        right_widget.setLayout(QVBoxLayout())
        right_widget.layout().addWidget(results_group)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 350])
        
        main_layout.addWidget(splitter)
        
        # Variáveis para arrastar a janela
        self.drag_position = None
        
        # Calcular e plotar com valores padrão
        self.calculate_and_plot()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
	
    def get_input_style(self):
        return f"""
            QDoubleSpinBox, QSpinBox, QComboBox {{
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 3px;  /* Padding menor */
                min-height: 24px;  /* Altura mínima um pouco maior */
            }}
            QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{
                border: 1px solid {COLORS['accent']};
            }}
        """
    
    def toggle_tax_rate(self, state):
        self.dividend_tax_rate.setEnabled(state == Qt.Checked)
    
    def update_contribution_label(self):
        if self.contribution_type.currentIndex() == 0:
            self.contribution_label.setText("Monthly Contribution ($):")
        else:
            self.contribution_label.setText("Annual Contribution ($):")
    
    # Método view_chart modificado
    def view_chart(self, chart_type):
        """Abrir o arquivo HTML do gráfico no navegador"""
        if chart_type in self.html_files:
            file_path = self.html_files[chart_type]
            if os.path.exists(file_path):
                try:
                    # Tentar abrir no navegador
                    webbrowser.open('file://' + file_path)
                    
                    # Mostrar mensagem de confirmação com o caminho
                    QMessageBox.information(
                        self, 
                        "Graph Saved", 
                        f"Graph saved and opened.\nLocation: {file_path}"
                    )
                except Exception as e:
                    # Se falhar, mostrar apenas o caminho
                    QMessageBox.information(
                        self, 
                        "Graph Saved", 
                        f"Graph saved but couldn't open automatically.\nPlease open manually from: {file_path}\nError: {str(e)}"
                    )
            else:
                QMessageBox.warning(
                    self, 
                    "File Not Found", 
                    f"Graph file not found: {file_path}"
                )

    
    def calculate_and_plot(self):
        # Obter valores de entrada
        starting_principal = self.starting_principal.value()
        annual_dividend_yield = self.annual_dividend_yield.value() / 100
        is_taxed = self.is_taxed.isChecked()
        dividend_tax_rate = self.dividend_tax_rate.value() / 100 if is_taxed else 0
        expected_annual_dividend_increase = self.expected_annual_dividend_increase.value() / 100
        payment_frequency_idx = self.dividend_payment_frequency.currentIndex()
        payment_frequency = [12, 4, 1][payment_frequency_idx]  # Mensal, Trimestral, Anual
        payment_frequency_names = ["Monthly", "Quarterly", "Yearly"]
        
        contribution_type_idx = self.contribution_type.currentIndex()
        periodic_contribution = self.periodic_contribution.value()
        # Ajustar contribuição anual para contribuição mensal para cálculos internos
        if contribution_type_idx == 1:  # Contribuição Anual
            monthly_contribution = periodic_contribution / 12
        else:  # Contribuição Mensal
            monthly_contribution = periodic_contribution
        
        years_invested = self.years_invested.value()
        dividend_reinvestment = self.dividend_reinvestment.isChecked()
        expected_annual_share_price_appreciation = self.expected_annual_share_price_appreciation.value() / 100
        
        # Calcular resultados
        months = years_invested * 12
        
        # Arrays para armazenar resultados
        portfolio_values = np.zeros(months + 1)
        dividend_income = np.zeros(months + 1)
        yield_on_cost = np.zeros(months + 1)
        cumulative_contributions = np.zeros(months + 1)
        cumulative_dividends = np.zeros(months + 1)
        
        # Valores iniciais
        portfolio_values[0] = starting_principal
        yield_on_cost[0] = annual_dividend_yield * 100
        cumulative_contributions[0] = starting_principal
        
        current_principal = starting_principal
        current_yield = annual_dividend_yield
        
        # Loop mensal para cálculos
        for month in range(1, months + 1):
            # Adicionar contribuição mensal
            current_principal += monthly_contribution
            cumulative_contributions[month] = cumulative_contributions[month-1] + monthly_contribution
            
            # Calcular pagamento de dividendos neste mês
            if month % (12 // payment_frequency) == 0:  # Verificar se é um mês de pagamento de dividendos
                # Ajustar taxa anual para o período de pagamento
                period_yield = current_yield / payment_frequency
                dividend_payment = current_principal * period_yield
                
                # Aplicar impostos se necessário
                if is_taxed:
                    dividend_payment *= (1 - dividend_tax_rate)
                
                # Armazenar renda de dividendos
                dividend_income[month] = dividend_payment
                cumulative_dividends[month] = cumulative_dividends[month-1] + dividend_payment
                
                # Reinvestir dividendos se habilitado
                if dividend_reinvestment:
                    current_principal += dividend_payment
            else:
                dividend_income[month] = 0
                cumulative_dividends[month] = cumulative_dividends[month-1]
            
            # Aplicar valorização mensal das ações (composta mensalmente)
            monthly_appreciation = (1 + expected_annual_share_price_appreciation) ** (1/12) - 1
            current_principal *= (1 + monthly_appreciation)
            
            # Atualizar taxa de dividendos anualmente
            if month % 12 == 0:
                current_yield *= (1 + expected_annual_dividend_increase)
            
            # Armazenar valor do portfólio e yield on cost
            portfolio_values[month] = current_principal
            if cumulative_contributions[month] > 0:
                annual_dividend = current_principal * current_yield
                if is_taxed:
                    annual_dividend *= (1 - dividend_tax_rate)
                yield_on_cost[month] = (annual_dividend / cumulative_contributions[month]) * 100
            else:
                yield_on_cost[month] = 0
        
        # Converter para meses e anos para plotagem
        months_array = np.arange(months + 1)
        years_array = months_array / 12
        
        # Criar dataframe para plotagem
        df = pd.DataFrame({
            'Years': years_array,
            'Portfolio Value': portfolio_values,
            'Cumulative Contributions': cumulative_contributions,
            'Cumulative Dividends': cumulative_dividends,
            'Appreciation': portfolio_values - cumulative_contributions - cumulative_dividends,
            'Dividend Income': dividend_income,
            'Yield on Cost': yield_on_cost
        })
        
        self.df_results = df.copy()
		
        # Plotar resultados
        self.plot_portfolio_balance(df)
        self.plot_dividend_income(df, payment_frequency_names[payment_frequency_idx])
        self.plot_yield_on_cost(df)
    
    def plot_portfolio_balance(self, df):
        # Criar o gráfico
        fig = go.Figure()
        
        # Adicionar traços para cada linha
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=df['Portfolio Value'],
            mode='lines',
            name='Total Portfolio Value',
            line=dict(color=COLORS['graph1'], width=3),
            hovertemplate='Year: %{x:.1f}<br>Portfolio Value: $%{y:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=df['Cumulative Contributions'],
            mode='lines',
            name='Cumulative Contributions',
            line=dict(color=COLORS['graph2'], width=2, dash='dash'),
            hovertemplate='Year: %{x:.1f}<br>Contributions: $%{y:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=df['Cumulative Dividends'],
            mode='lines',
            name='Cumulative Dividends',
            line=dict(color=COLORS['graph3'], width=2, dash='dot'),
            hovertemplate='Year: %{x:.1f}<br>Dividends: $%{y:,.2f}<extra></extra>'
        ))
        
        # Adicionar área para valorização
        contributed_plus_dividends = df['Cumulative Contributions'] + df['Cumulative Dividends']
        
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=df['Portfolio Value'],
            mode='lines',
            name='Appreciation',
            fill='tonexty',
            fillcolor=f'rgba({int(COLORS["graph4"][1:3], 16)}, {int(COLORS["graph4"][3:5], 16)}, {int(COLORS["graph4"][5:7], 16)}, 0.2)',
            line=dict(width=0),
            hovertemplate='Year: %{x:.1f}<br>Appreciation: $%{y:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=contributed_plus_dividends,
            mode='lines',
            showlegend=False,
            line=dict(width=0),
            hoverinfo='skip'
        ))
        
        # Atualizar layout
        fig.update_layout(
            title='Portfolio Balance Over Time',
            xaxis_title='Years',
            yaxis_title='Value ($)',
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_white",
            autosize=True,
            height=700
        )
        
        # Adicionar anotação de valor final
        final_row = df.iloc[-1]
        final_value = final_row['Portfolio Value']
        total_contributions = final_row['Cumulative Contributions']
        total_dividends = final_row['Cumulative Dividends']
        total_appreciation = final_value - total_contributions - total_dividends
        
        annotation_text = (
            f"Final Value: ${final_value:,.2f}<br>"
            f"Contributions: ${total_contributions:,.2f} ({total_contributions/final_value*100:.1f}%)<br>"
            f"Dividends: ${total_dividends:,.2f} ({total_dividends/final_value*100:.1f}%)<br>"
            f"Appreciation: ${total_appreciation:,.2f} ({total_appreciation/final_value*100:.1f}%)"
        )
        
        fig.add_annotation(
            x=0.02,
            y=0.02,
            xref="paper",
            yref="paper",
            text=annotation_text,
            showarrow=False,
            font=dict(size=10),
            align="left",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#2c3e50",
            borderwidth=1,
            borderpad=4
        )
        
        # Salvar o gráfico como HTML
        pio.write_html(fig, file=self.html_files['portfolio'], auto_open=False)
    
    def plot_dividend_income(self, df, frequency):
        # Criar o gráfico
        fig = go.Figure()
        
        # Calcular média móvel de dividendos para visão anualizada
        window_size = 12  # Média anual
        dividend_income_smoothed = df['Dividend Income'].rolling(window=window_size, min_periods=1).sum()
        
        # Adicionar barras para pagamentos de dividendos
        fig.add_trace(go.Bar(
            x=df['Years'], 
            y=df['Dividend Income'],
            name=f'{frequency} Dividends',
            marker_color=f'rgba({int(COLORS["graph3"][1:3], 16)}, {int(COLORS["graph3"][3:5], 16)}, {int(COLORS["graph3"][5:7], 16)}, 0.4)',
            hovertemplate='Year: %{x:.1f}<br>Dividend Payment: $%{y:,.2f}<extra></extra>'
        ))
        
        # Adicionar linha para dividendos anualizados
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=dividend_income_smoothed,
            mode='lines',
            name='Annualized Dividends',
            line=dict(color=COLORS['graph3'], width=3),
            customdata=dividend_income_smoothed/12,
            hovertemplate='Year: %{x:.1f}<br>Annual Income: $%{y:,.2f}<br>Monthly Average: $%{customdata:,.2f}<extra></extra>'
        ))
        
        # Atualizar layout
        fig.update_layout(
            title='Dividend Income Over Time',
            xaxis_title='Years',
            yaxis_title='Value ($)',
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_white",
            autosize=True,
            height=700
        )
        
        # Adicionar anotação de valor final
        last_payment = df['Dividend Income'].iloc[-1]
        last_annualized = dividend_income_smoothed.iloc[-1]
        
        annotation_text = (
            f"Last Payment: ${last_payment:,.2f}<br>"
            f"Annual Income: ${last_annualized:,.2f}<br>"
            f"Monthly Average: ${last_annualized/12:,.2f}"
        )
        
        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            text=annotation_text,
            showarrow=False,
            font=dict(size=10),
            align="left",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#2c3e50",
            borderwidth=1,
            borderpad=4
        )
        
        # Salvar o gráfico como HTML
        pio.write_html(fig, file=self.html_files['dividend'], auto_open=False)
    
    def plot_yield_on_cost(self, df):
        # Criar o gráfico
        fig = go.Figure()
        
        # Adicionar linha para yield on cost
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=df['Yield on Cost'],
            mode='lines',
            name='Yield on Cost',
            line=dict(color=COLORS['graph2'], width=3),
            hovertemplate='Year: %{x:.1f}<br>Yield on Cost: %{y:.2f}%<extra></extra>'
        ))
        
        # Adicionar linha para rendimento inicial
        initial_yield = df['Yield on Cost'].iloc[0]
        
        fig.add_trace(go.Scatter(
            x=df['Years'], 
            y=[initial_yield] * len(df),
            mode='lines',
            name=f'Initial Yield ({initial_yield:.2f}%)',
            line=dict(color=COLORS['graph4'], width=2, dash='dash'),
            hoverinfo='skip'
        ))
        
        # Atualizar layout
        fig.update_layout(
            title='Yield on Cost Over Time',
            xaxis_title='Years',
            yaxis_title='Yield (%)',
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_white",
            autosize=True,
            height=700
        )
        
        # Adicionar anotação de valores finais
        final_yield = df['Yield on Cost'].iloc[-1]
        increase = (final_yield / initial_yield - 1) * 100
        
        # Calcular renda anual estimada para valor final
        final_portfolio = df['Portfolio Value'].iloc[-1]
        estimated_annual_income = (final_yield / 100) * df['Cumulative Contributions'].iloc[-1]
        
        annotation_text = (
            f"Initial Yield: {initial_yield:.2f}%<br>"
            f"Final Yield: {final_yield:.2f}%<br>"
            f"Increase: {increase:.1f}%<br>"
            f"Est. Annual Income: ${estimated_annual_income:,.2f}"
        )
        
        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            text=annotation_text,
            showarrow=False,
            font=dict(size=10),
            align="left",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#2c3e50",
            borderwidth=1,
            borderpad=4
        )
        
        # Salvar o gráfico como HTML
        pio.write_html(fig, file=self.html_files['yield'], auto_open=False)
		
    def view_results_table(self):
        """
        Cria e exibe uma tabela HTML com todos os resultados calculados por período.
        A tabela é salva como HTML e aberta no navegador.
        """
        if not hasattr(self, 'df_results') or self.df_results is None:
            QMessageBox.warning(
                self, 
                "No Data", 
                "Please calculate the results first."
            )
            return
        
        # Criar um dataframe formatado para exibição
        df_display = self.df_results.copy()
        
        # Arredondar os anos para 1 casa decimal
        df_display['Years'] = df_display['Years'].round(1)
        
        # Selecionar apenas os anos completos e o final para reduzir o tamanho da tabela
        years_to_show = list(range(0, len(df_display), 12))  # Mostrar anos completos
        if len(df_display) - 1 not in years_to_show:  # Adicionar o último período se não estiver incluído
            years_to_show.append(len(df_display) - 1)
        
        df_display = df_display.iloc[years_to_show].copy()
        
        # Formatar os valores para exibição
        df_display['Portfolio Value'] = df_display['Portfolio Value'].map('${:,.2f}'.format)
        df_display['Cumulative Contributions'] = df_display['Cumulative Contributions'].map('${:,.2f}'.format)
        df_display['Cumulative Dividends'] = df_display['Cumulative Dividends'].map('${:,.2f}'.format)
        df_display['Appreciation'] = df_display['Appreciation'].map('${:,.2f}'.format)
        
        # Calcular valores anuais e mensais de dividendos para cada período selecionado
        annual_income = []
        monthly_income = []
        
        for idx in years_to_show:
            if idx < 12:
                # Para o primeiro ano, pegar a soma dos primeiros 12 meses ou menos
                annual_sum = self.df_results['Dividend Income'].iloc[:idx+1].sum()
            else:
                # Para os anos seguintes, pegar a soma dos 12 meses anteriores
                annual_sum = self.df_results['Dividend Income'].iloc[idx-11:idx+1].sum()
            
            annual_income.append(annual_sum)
            monthly_income.append(annual_sum / 12)
        
        df_display['Annual Dividend Income'] = annual_income
        df_display['Annual Dividend Income'] = df_display['Annual Dividend Income'].map('${:,.2f}'.format)
        
        df_display['Monthly Dividend Income'] = monthly_income
        df_display['Monthly Dividend Income'] = df_display['Monthly Dividend Income'].map('${:,.2f}'.format)
        
        df_display['Yield on Cost'] = df_display['Yield on Cost'].map('{:.2f}%'.format)
        
        # Renomear colunas para exibição
        df_display = df_display.rename(columns={
            'Years': 'Year',
            'Portfolio Value': 'Portfolio Value',
            'Cumulative Contributions': 'Total Contributions',
            'Cumulative Dividends': 'Total Dividends',
            'Appreciation': 'Total Appreciation',
            'Yield on Cost': 'Yield on Cost'
        })
        
        # Criar tabela HTML com estilo
        html_table = df_display.to_html(index=False)
        
        # Adicionar estilos CSS para a tabela
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dividend Calculator Results</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                    background-color: white;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: right;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                tr:hover {{
                    background-color: #e0f7fa;
                }}
                .header-row {{
                    position: sticky;
                    top: 0;
                }}
                .summary {{
                    margin-top: 20px;
                    padding: 15px;
                    background-color: #e8f4f8;
                    border-radius: 5px;
                    border-left: 5px solid #3498db;
                }}
            </style>
        </head>
        <body>
            <h1>Dividend Portfolio Calculator Results</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Initial Investment:</strong> ${self.starting_principal.value():,.2f}</p>
                <p><strong>Monthly Contribution:</strong> ${self.periodic_contribution.value() if self.contribution_type.currentIndex() == 0 else self.periodic_contribution.value()/12:,.2f}</p>
                <p><strong>Years Invested:</strong> {self.years_invested.value()}</p>
                <p><strong>Initial Dividend Yield:</strong> {self.annual_dividend_yield.value()}%</p>
                <p><strong>Expected Annual Dividend Increase:</strong> {self.expected_annual_dividend_increase.value()}%</p>
                <p><strong>Expected Annual Share Price Appreciation:</strong> {self.expected_annual_share_price_appreciation.value()}%</p>
                <p><strong>Dividend Reinvestment:</strong> {'Yes' if self.dividend_reinvestment.isChecked() else 'No'}</p>
                <p><strong>Dividend Payment Frequency:</strong> {['Monthly', 'Quarterly', 'Yearly'][self.dividend_payment_frequency.currentIndex()]}</p>
            </div>
            
            {html_table}
            
            <div class="summary">
                <p>This table shows results at yearly intervals. For more detailed data and interactive visualizations, 
                please use the chart views.</p>
            </div>
        </body>
        </html>
        """
        
        # Salvar a tabela HTML
        table_file = os.path.join(self.graphs_folder, 'results_table.html')
        with open(table_file, 'w') as f:
            f.write(html_content)
        
        # Abrir no navegador
        try:
            webbrowser.open('file://' + table_file)
            QMessageBox.information(
                self, 
                "Table Generated", 
                f"Results table generated and opened.\nLocation: {table_file}"
            )
        except Exception as e:
            QMessageBox.information(
                self, 
                "Table Generated", 
                f"Results table generated but couldn't open automatically.\nPlease open manually from: {table_file}\nError: {str(e)}"
            )

    def show_donate_dialog(self):
        """Exibe a janela de doação"""
        donate_dialog = DonateDialog(self)
        donate_dialog.exec_()
			
class DonateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Support This Project")
        self.setMinimumWidth(450)
        
        # Utilizando a mesma paleta de cores do app principal
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QLabel#title {{
                font-size: 18px;
                font-weight: bold;
                color: {COLORS['primary']};
            }}
            QLabel#address {{
                font-family: monospace;
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                selection-background-color: {COLORS['secondary']};
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Support Dividend Portfolio Calculator")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        description = QLabel(
            "If you find this tool useful, please consider making a donation. "
            "Your support helps maintain and improve this application."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        # Bitcoin logo and QR code in a horizontal layout
        donation_layout = QHBoxLayout()
        
        # Create Bitcoin logo
        bitcoin_logo = self.create_bitcoin_logo()
        donation_layout.addWidget(bitcoin_logo)
        
        # Create QR code
        qr_label = self.create_qr_code("bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l")
        donation_layout.addWidget(qr_label)
        
        layout.addLayout(donation_layout)
        
        # Bitcoin address
        address_frame = QFrame()
        address_frame.setStyleSheet(f"background-color: white; border-radius: 8px; padding: 10px;")
        address_layout = QVBoxLayout(address_frame)
        
        address_title = QLabel("Bitcoin Address:")
        address_title.setStyleSheet("font-weight: bold;")
        address_layout.addWidget(address_title)
        
        address_label = QLabel("bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l")
        address_label.setObjectName("address")
        address_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        address_label.setCursor(Qt.IBeamCursor)
        address_layout.addWidget(address_label)
        
        copy_info = QLabel("Click the address to select it, then copy with Ctrl+C")
        copy_info.setStyleSheet(f"color: {COLORS['text']}; font-size: 11px;")
        address_layout.addWidget(copy_info)
        
        layout.addWidget(address_frame)
        
        # Thank you message
        thanks = QLabel("Thank you for your support!")
        thanks.setAlignment(Qt.AlignCenter)
        thanks.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(thanks)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setMinimumWidth(100)
        close_button.setMinimumHeight(36)
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def create_qr_code(self, data):
        """Create a QR code for the given data"""
        # Criar QR code com tamanho maior e borda menor
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Criar a imagem usando PIL
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter a imagem PIL para um formato que o PyQt5 possa usar
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Carregar a imagem como QPixmap
        qr_pixmap = QPixmap()
        qr_pixmap.loadFromData(buffer.getvalue())
        
        # Criar QLabel com o QR code
        qr_label = QLabel()
        qr_label.setPixmap(qr_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        qr_label.setAlignment(Qt.AlignCenter)
        
        return qr_label
    
    def create_bitcoin_logo(self):
        """Create a Bitcoin logo with proper circle"""
        # Criar um QLabel para exibir o logo
        bitcoin_label = QLabel()
        bitcoin_label.setFixedSize(120, 120)
        
        # Criar um QPixmap para desenhar o logo
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)  # Fundo transparente
        
        # Iniciar o painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # Para melhorar a qualidade
        
        # Definir cores
        bitcoin_orange = QColor("#F7931A")
        
        # Desenhar círculo de fundo
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bitcoin_orange))
        painter.drawEllipse(10, 10, 100, 100)
        
        # Configurar a fonte para o símbolo ₿
        font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(font)
        
        # Desenhar símbolo ₿ em branco
        painter.setPen(QColor("white"))
        
        # Criar um retângulo para centralizar o texto
        text_rect = QRect(10, 10, 100, 100)
        painter.drawText(text_rect, Qt.AlignCenter, "₿")
        
        # Finalizar o painter
        painter.end()
        
        # Definir o pixmap como imagem do QLabel
        bitcoin_label.setPixmap(pixmap)
        bitcoin_label.setAlignment(Qt.AlignCenter)
        
        return bitcoin_label

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    window = DividendPortfolioCalculator()
    window.show()
    sys.exit(app.exec_())