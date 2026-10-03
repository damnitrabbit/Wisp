import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5Terms';
import M from '@/v5/screens/V5MTerms';

export const metadata = { title: 'The rules', alternates: { canonical: '/terms' } };

export default function Terms() {
  return <Screen desktop={D} phone={M} />;
}
