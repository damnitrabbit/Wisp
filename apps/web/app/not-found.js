import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5NotFound';
import M from '@/v5/screens/V5MNotFound';

export const metadata = { title: "This note isn't here" };

export default function NotFound() {
  return <Screen desktop={D} phone={M} />;
}
