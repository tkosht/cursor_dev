// public/elements/SimpleForm.jsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SimpleForm() {
  const [values, setValues] = React.useState({ name: "", due: "" });
  const [timeLeft, setTimeLeft] = React.useState(props.timeout || 30);

  React.useEffect(() => {
    const t = setInterval(() => setTimeLeft((s) => (s > 0 ? s - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <Card id="simple-form" className="w-full max-w-xl">
      <CardHeader>
        <CardTitle>入力フォーム（残り {timeLeft}s）</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-3">
        <div className="grid gap-1">
          <Label htmlFor="name">お名前 *</Label>
          <Input id="name" value={values.name} onChange={(e) => setValues({ ...values, name: e.target.value })} />
        </div>
        <div className="grid gap-1">
          <Label htmlFor="due">期限</Label>
          <Input id="due" type="date" value={values.due} onChange={(e) => setValues({ ...values, due: e.target.value })} />
        </div>
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        <Button id="cancel" variant="outline" onClick={() => cancelElement()}>
          Cancel
        </Button>
        <Button
          id="submit"
          disabled={!values.name}
          onClick={() => submitElement({ submitted: true, ...values })}
        >
          Submit
        </Button>
      </CardFooter>
    </Card>
  );
}
