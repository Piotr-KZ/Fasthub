import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Steps, message } from 'antd';
import { BankOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import { organizationsApi } from '../api/organizations';

const { Title, Paragraph } = Typography;

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // Create organization via backend
      await organizationsApi.create({
        name: values.organization_name,
      });
      
      message.success('Organization created successfully!');
      navigate('/dashboard');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to create organization');
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      title: 'Organization Details',
      description: 'Set up your organization',
    },
  ];

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <Card style={{ width: 600, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2}>Welcome to FastHub! 🎉</Title>
          <Paragraph type="secondary">
            Let's set up your organization to get started
          </Paragraph>
        </div>

        <Steps current={currentStep} items={steps} style={{ marginBottom: 32 }} />

        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
        >
          <Form.Item
            name="organization_name"
            label="Organization Name"
            rules={[{ required: true, message: 'Please enter your organization name!' }]}
          >
            <Input 
              prefix={<BankOutlined />} 
              placeholder="Acme Inc." 
              size="large"
            />
          </Form.Item>



          <Form.Item style={{ marginTop: 32 }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              size="large"
              loading={loading}
            >
              Complete Setup
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Paragraph type="secondary" style={{ fontSize: 12 }}>
              You can update these details later in Settings
            </Paragraph>
          </div>
        </Form>
      </Card>
    </div>
  );
}
