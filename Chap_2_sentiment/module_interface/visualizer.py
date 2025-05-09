import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.SQL_query import sql_operation


class visualizer:
    def __init__(self):
        sql = sql_operation()
        self.df = sql.get_info('SAC_THAI')
        self.bank = sql.get_info('NGAN_HANG')['Ten'].tolist()
        self.topic = sql.get_info('CHU_DE')['Ten'].tolist()

        self.df['Ngay'] = pd.to_datetime(self.df['Ngay'])
        self.df['ngan_hang'] = self.df['ngan_hang'].apply(lambda x: 'Không chứa ngân hàng' if x is None else x)
        self.bank.append('Không chứa ngân hàng')

    def default_handler(self):
        fig = go.Figure()
        # Text display
        fig.add_annotation(
            text="<b>Vui lòng chọn ít nhất một chủ đề hoặc ngân hàng cụ thể</b>",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, family="Times New Roman", color='indianred')
        )
        # Blank layout
        fig.update_layout(
            height=250,
            xaxis={'visible': False},
            yaxis={'visible': False},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        # fig.show()
        return fig

    def nothing_handler(self):
        fig = go.Figure()
        # Text display
        fig.add_annotation(
            text="<b>Không có dữ liệu bài viết nào</b>",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, family="Times New Roman", color='indianred')
        )
        # Blank layout
        fig.update_layout(
            height=250,
            xaxis={'visible': False},
            yaxis={'visible': False},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        # fig.show()
        return fig

    def barplot(self, df_searched, bank, topic):
        # Count the number of each sentiment and sort them
        counts = df_searched['sac_thai'].value_counts()
        order = ['tiêu cực', 'trung lập', 'tích cực']
        counts = counts.reindex(order).fillna(0)
        # Calculate the percentage of each sentiment
        total = counts.sum()
        percentages = counts / total * 100
        # Plotting
        colors = ['red', 'grey', 'green']
        bar = go.Figure()
        left = 0  # left edge of each bar
        # Loop through each sentiment and stack the bars
        for i, (category, percentage) in enumerate(percentages.items()):
            bar.add_trace(go.Bar(
                y=[f'Tổng: {int(total)} bài viết'],
                x=[percentage],
                orientation='h',
                name=category,
                marker=dict(color=colors[i]),
                text=[f'{percentage:.0f}%'],
                hoverinfo='text',
                hovertemplate=f'{int(counts[i])} bài viết',
                textposition='inside',
                insidetextanchor='middle',
                showlegend=False
            ))
            left += percentage
        return bar

    def legend_config(self):
        return dict(
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1
        )

    def display_both(self, df_date, bank, topic):
        df_searched = df_date.loc[(df_date['ngan_hang'] == bank) & (df_date['chu_de'] == topic)]
        total = len(df_searched)
        if total == 0:
            return self.nothing_handler()
        num_row = 1
        fig = make_subplots(rows=num_row, cols=1)
        stacked_bar = self.barplot(df_searched, bank, topic)
        for trace in stacked_bar.data:
            trace.showlegend = True
            fig.add_trace(trace, row=1, col=1)
        fig.update_yaxes(side='right', tickfont=dict(size=16), tickprefix="  ", row=1, col=1)
        fig.update_xaxes(range=[0, 100], tickvals=[], row=1, col=1)
        # Set layout
        fig.update_layout(
            height=125*(num_row+1),
            barmode='stack',
            title=f'<b>Sắc thái thảo luận {bank} - Chủ đề: {topic}</b>',
            title_font_color="firebrick",
            font=dict(size=16, family="Times New Roman"),
            legend=self.legend_config()
        )
        # fig.show()
        return fig

    def display_bank(self, df_date, bank):
        df_searched = df_date.loc[(df_date['ngan_hang'] == bank)]
        # Check all topics related
        non_empty = []
        for i in range(len(self.topic)):
            df_temp = df_searched.loc[df_searched['chu_de'] == self.topic[i]]
            if len(df_temp) > 0:
                non_empty.append(self.topic[i])
        num_row = len(non_empty)
        if num_row == 0:
            return self.nothing_handler()
        # Plotting
        num_row += 1
        non_empty.insert(0, 'Tất cả')
        fig = make_subplots(rows=num_row, cols=1, subplot_titles=non_empty)
        # Loop through all topics
        for i in range(num_row):
            topic = non_empty[i]
            if i == 0:
                df_temp = df_searched
            else:
                df_temp = df_searched.loc[df_searched['chu_de'] == topic]
            stacked_bar = self.barplot(df_temp, bank, topic)
            for trace in stacked_bar.data:
                if i == 0:
                    trace.showlegend = True
                fig.add_trace(trace, row=i+1, col=1)
            fig.update_yaxes(side='right', tickfont=dict(size=16), tickprefix="  ", row=i+1, col=1)
            fig.update_xaxes(range=[0, 100], tickvals=[], row=i+1, col=1)
        fig.for_each_annotation(lambda x: x.update(text="Chủ đề: " + x.text))
        # Set layout
        fig.update_layout(
            height=125*(num_row+1),
            barmode='stack',
            title=f'<b>Sắc thái thảo luận {bank}</b>',
            title_font_color="firebrick",
            font=dict(size=16, family="Times New Roman"),
            legend=self.legend_config()
        )
        # fig.show()
        return fig

    def display_topic(self, df_date, topic):
        df_searched = df_date.loc[(df_date['chu_de'] == topic)]
        # Check all banks related
        non_empty = []
        for i in range(len(self.bank)):
            df_temp = df_searched.loc[df_searched['ngan_hang'] == self.bank[i]]
            if len(df_temp) > 0:
                non_empty.append(self.bank[i])
        num_row = len(non_empty)
        if num_row == 0:
            return self.nothing_handler()
        # Plotting
        num_row += 1
        non_empty.insert(0, 'Tất cả ngân hàng')
        fig = make_subplots(rows=num_row, cols=1, subplot_titles=non_empty)
        # Loop through all topics
        for i in range(num_row):
            bank = non_empty[i]
            if i == 0:
                df_temp = df_searched
            else:
                df_temp = df_searched.loc[df_searched['ngan_hang'] == bank]
            stacked_bar = self.barplot(df_temp, bank, topic)
            for trace in stacked_bar.data:
                if i == 0:
                    trace.showlegend = True
                fig.add_trace(trace, row=i+1, col=1)
            fig.update_yaxes(side='right', tickfont=dict(size=16), tickprefix="  ", row=i+1, col=1)
            fig.update_xaxes(range=[0, 100], tickvals=[], row=i+1, col=1)
        # Set layout
        fig.update_layout(
            height=125*(num_row+1),
            barmode='stack',
            title=f'<b>Sắc thái thảo luận về chủ đề {topic}</b>',
            title_font_color="firebrick",
            font=dict(size=16, family="Times New Roman"),
            legend=self.legend_config()
        )
        # fig.show()
        return fig

    def display(self, bank=None, topic=None, date_start=None, date_end=None):
        df_date = self.df.loc[(self.df['Ngay'] >= date_start) & (self.df['Ngay'] <= date_end)]

        if bank != 'Tất cả' and topic != 'Tất cả':
            return self.display_both(df_date, bank, topic)

        elif bank != 'Tất cả':
            return self.display_bank(df_date, bank)

        elif topic != 'Tất cả':
            return self.display_topic(df_date, topic)

        else:
            return self.default_handler()


# if __name__ == '__main__':
#     c = controller()
#     c.display('Ngân hàng TMCP Ngoại thương Việt Nam', 'Tiền gửi tiết kiệm', datetime(2022, 1, 1), datetime(2024, 1, 1))
#     c.display('Ngân hàng TMCP Ngoại thương Việt Nam', "Tất cả", datetime(2022, 1, 1), datetime(2024, 1, 1))
#     c.display("Tất cả", "Tiền gửi tiết kiệm", datetime(2022, 1, 1), datetime(2024, 1, 1))
#     c.display("Tất cả", "Tất cả", datetime(2022, 1, 1), datetime(2024, 1, 1))
