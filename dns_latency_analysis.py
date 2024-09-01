import pandas as pd
import matplotlib.pyplot as plt
import os

# Detailed analysis function with plots and detailed statistics
def detailed_analysis(file_path='dns_latency_results.csv', save_plots=True, output_dir='plots'):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print("No data available for analysis.")
        return

    df = pd.read_csv(file_path)

    if df.empty:
        print("No data available for analysis.")
        return

    # Convert timestamp to datetime and sort by it
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

    # Ensure that 'ping_latency_nan_count', 'google_query_latency_nan_count', 'domain_query_latency_nan_count' are correctly created
    df['ping_latency_nan_count'] = df['ping_latency'].isna().astype(int)
    df['google_query_latency_nan_count'] = df['google_query_latency'].isna().astype(int)
    df['domain_query_latency_nan_count'] = df['domain_query_latency'].isna().astype(int)

    # Calculate the global maximum latency across all servers and latency types
    global_max_latency = df[['ping_latency', 'google_query_latency', 'domain_query_latency']].max().max()

    # Create output directory if saving plots
    if save_plots and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ### Individual Server Plots
    # Plot latency over time for each server (ping, google.com, and random domain)
    for server in df['server'].unique():
        server_df = df[df['server'] == server]

        plt.figure(figsize=(19.2, 10.8))  # Set figsize for Full HD resolution
        plt.plot(server_df['timestamp'], server_df['ping_latency'], label='Ping Latency')
        plt.plot(server_df['timestamp'], server_df['google_query_latency'], label='Google.com Latency')
        plt.plot(server_df['timestamp'], server_df['domain_query_latency'], label=f'Random Domain Latency ({server_df["domain"].iloc[0]})')

        plt.title(f'Latency over time for {server}')
        plt.xlabel('Timestamp')
        plt.ylabel('Latency (s)')
        plt.ylim(0, global_max_latency)  # Set consistent y-axis limits for all plots
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        if save_plots:
            plot_filename = f"{output_dir}/latency_{server.replace(':', '_')}.png"
            plt.savefig(plot_filename, dpi=100)  # Save with DPI set to 100 for Full HD resolution
            print(f"Saved plot for {server} as {plot_filename}")
            plt.close()  # Close the figure after saving to free memory
        else:
            plt.show()

    ### Grouped Line Graphs by Latency Type
    # Ping Latency - Grouped by servers
    plt.figure(figsize=(19.2, 10.8))
    for server in df['server'].unique():
        server_df = df[df['server'] == server]
        plt.plot(server_df['timestamp'], server_df['ping_latency'], label=server)
    plt.title('Ping Latency over Time (Grouped by Servers)')
    plt.xlabel('Timestamp')
    plt.ylabel('Latency (s)')
    plt.ylim(0, df['ping_latency'].max())  # Dynamic y-axis limit based on actual data
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    if save_plots:
        plot_filename = f"{output_dir}/ping_latency_grouped.png"
        plt.savefig(plot_filename, dpi=100)
        print(f"Saved grouped ping latency plot as {plot_filename}")
        plt.close()
    else:
        plt.show()

    # Google Query Latency - Grouped by servers
    plt.figure(figsize=(19.2, 10.8))
    for server in df['server'].unique():
        server_df = df[df['server'] == server]
        plt.plot(server_df['timestamp'], server_df['google_query_latency'], label=server)
    plt.title('Google Query Latency over Time (Grouped by Servers)')
    plt.xlabel('Timestamp')
    plt.ylabel('Latency (s)')
    plt.ylim(0, df['google_query_latency'].max())  # Dynamic y-axis limit based on actual data
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    if save_plots:
        plot_filename = f"{output_dir}/google_latency_grouped.png"
        plt.savefig(plot_filename, dpi=100)
        print(f"Saved grouped Google query latency plot as {plot_filename}")
        plt.close()
    else:
        plt.show()

    # New Domain Query Latency - Grouped by servers
    plt.figure(figsize=(19.2, 10.8))
    for server in df['server'].unique():
        server_df = df[df['server'] == server]
        plt.plot(server_df['timestamp'], server_df['domain_query_latency'], label=server)
    plt.title('New Domain Query Latency over Time (Grouped by Servers)')
    plt.xlabel('Timestamp')
    plt.ylabel('Latency (s)')
    plt.ylim(0, df['domain_query_latency'].max())  # Dynamic y-axis limit based on actual data
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    if save_plots:
        plot_filename = f"{output_dir}/domain_latency_grouped.png"
        plt.savefig(plot_filename, dpi=100)
        print(f"Saved grouped new domain query latency plot as {plot_filename}")
        plt.close()
    else:
        plt.show()

    ### Summary Bar Graphs for Comparison
    # Compute summary statistics for each server
    summary = df.groupby('server').agg({
        'ping_latency': ['mean', 'median', 'std'],
        'google_query_latency': ['mean', 'median', 'std'],
        'domain_query_latency': ['mean', 'median', 'std']
    })

    summary.columns = [
        'ping_latency_mean', 'ping_latency_median', 'ping_latency_std',
        'google_query_latency_mean', 'google_query_latency_median', 'google_query_latency_std',
        'domain_query_latency_mean', 'domain_query_latency_median', 'domain_query_latency_std'
    ]

    # Aggregate statistics for all latency types
    summary['aggregate_mean'] = summary[['ping_latency_mean', 'google_query_latency_mean', 'domain_query_latency_mean']].mean(axis=1)
    summary['aggregate_median'] = summary[['ping_latency_median', 'google_query_latency_median', 'domain_query_latency_median']].mean(axis=1)
    summary['aggregate_std'] = summary[['ping_latency_std', 'google_query_latency_std', 'domain_query_latency_std']].mean(axis=1)

    # Ping Latency Comparison
    summary[['ping_latency_mean', 'ping_latency_median', 'ping_latency_std']].plot(kind='bar', figsize=(19.2, 10.8))
    plt.title('Ping Latency Comparison by Server (Mean, Median, Std)')
    plt.ylabel('Latency (s)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_plots:
        plot_filename = f"{output_dir}/ping_latency_comparison.png"
        plt.savefig(plot_filename, dpi=100)
        print(f"Saved ping latency comparison plot as {plot_filename}")
        plt.close()
    else:
        plt.show()

    # Google Query Latency Comparison
    summary[['google_query_latency_mean', 'google_query_latency_median', 'google_query_latency_std']].plot(kind='bar', figsize=(19.2, 10.8))
    plt.title('Google Query Latency Comparison by Server (Mean, Median, Std)')
    plt.ylabel('Latency (s)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_plots:
        plot_filename = f"{output_dir}/google_query_latency_comparison.png"
        plt.savefig(plot_filename, dpi=100)
        print(f"Saved Google query latency comparison plot as {plot_filename}")
        plt.close()
    else:
        plt.show()

    # New Domain Query Latency Comparison
    summary[['domain_query_latency_mean', 'domain_query_latency_median', 'domain_query_latency_std']].plot(kind='bar', figsize=(19.2, 10.8))
    plt.title('New Domain Query Latency Comparison by Server (Mean, Median, Std)')
    plt.ylabel('Latency (s)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_plots:
        plot_filename = f"{output_dir}/domain_query_latency_comparison.png"
        plt.savefig(plot_filename, dpi=100)
        print(f"Saved new domain query latency comparison plot as {plot_filename}")
        plt.close()
    else:
        plt.show()

    # Aggregate Latency Comparison
    summary[['aggregate_mean', 'aggregate_median', 'aggregate_std']].plot(kind='bar', figsize=(19.2, 10.8))
    plt.title('Aggregate Latency Comparison by Server (Mean, Median, Std)')
    plt.ylabel('Latency (s)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_plots:
        plot_filename = f"{output_dir}/aggregate_latency_comparison.png"
        plt.savefig(plot_filename, dpi=100)
        print(f"Saved aggregate latency comparison plot as {plot_filename}")
        plt.close()
    else:
        plt.show()

if __name__ == "__main__":
    detailed_analysis()
