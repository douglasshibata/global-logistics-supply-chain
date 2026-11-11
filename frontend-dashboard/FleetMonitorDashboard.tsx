import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface FleetTelemetry {
  vehicleId: string;
  latitude: number;
  longitude: number;
  speed: number;
  temperature: number;
}

export const FleetMonitorDashboard: React.FC = () => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current);

      // Opções iniciais do gráfico ECharts
      const option: echarts.EChartsOption = {
        title: { text: 'Monitoramento da Frota em Tempo Real', left: 'center' },
        tooltip: { trigger: 'item' },
        geo: {
          map: 'world',
          roam: true,
          label: { emphasis: { show: false } },
          itemStyle: {
            areaColor: '#323c48',
            borderColor: '#111',
            emphasis: { areaColor: '#2a333d' }
          }
        },
        series: [
          {
            name: 'Veículos Ativos',
            type: 'scatter',
            coordinateSystem: 'geo',
            data: [],
            symbolSize: 12,
            itemStyle: { color: '#00e676' }
          }
        ]
      };

      chartInstance.current.setOption(option);
    }

    // Conexão WebSocket com o barramento de eventos/Flink
    const ws = new WebSocket('ws://localhost:8080/ws/telemetry');

    ws.onmessage = (event) => {
      const data: FleetTelemetry = JSON.parse(event.data);

      if (chartInstance.current) {
        chartInstance.current.appendData({
          seriesIndex: 0,
          data: [
            {
              name: data.vehicleId,
              value: [data.longitude, data.latitude, data.temperature]
            }
          ]
        });
      }
    };

    return () => {
      ws.close();
      chartInstance.current?.dispose();
    };
  }, []);

  return <div ref={chartRef} style={{ width: '100%', height: '600px', backgroundColor: '#1a1a1a' }} />;
};
