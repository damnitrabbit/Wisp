import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5Privacy';
import M from '@/v5/screens/V5MPrivacy';

export const metadata = { title: 'What we keep', alternates: { canonical: '/privacy' } };

export default function Privacy() {
  return <Screen desktop={D} phone={M} />;
}
