import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Settings</h2>
        <p className="text-sm text-muted-foreground">
          Configuration is currently file-based. API-backed save is planned.
        </p>
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Project paths</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label>Chapters dir</Label>
              <Input defaultValue="chapters/" />
            </div>
            <div className="space-y-2">
              <Label>Lore dir</Label>
              <Input defaultValue="lore/" />
            </div>
            <div className="space-y-2">
              <Label>Excluded dirs</Label>
              <Textarea defaultValue=".bookops\nreports\n.git" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Reviewer defaults</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label>Reviewer handle</Label>
              <Input defaultValue="bookops-ui" />
            </div>
            <div className="space-y-2">
              <Label>Provider toggles</Label>
              <Textarea defaultValue="developmental_editor=true\ncontinuity_guardian=true" />
            </div>
            <Button variant="outline" disabled>
              Save settings (backend required)
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
