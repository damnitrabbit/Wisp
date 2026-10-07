import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5Help';
import M from '@/v5/screens/V5MHelp';

export const metadata = { title: 'Need help now?', alternates: { canonical: '/help' } };

export default function Help() {
  return <Screen desktop={D} phone={M} />;
}
