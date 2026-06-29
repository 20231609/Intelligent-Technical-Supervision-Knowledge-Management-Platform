import { ArrowUpOutlined } from "@ant-design/icons";
import { Typography } from "antd";

import "./StatusMetric.css";

type StatusMetricProps = {
  label: string;
  value: string;
  trend: string;
};

const { Text, Title } = Typography;

const StatusMetric = ({ label, value, trend }: StatusMetricProps) => {
  return (
    <div className="statusMetric">
      <Text type="secondary">{label}</Text>
      <Title level={3}>{value}</Title>
      <span className="statusMetricTrend">
        <ArrowUpOutlined />
        {trend}
      </span>
    </div>
  );
};

export default StatusMetric;
