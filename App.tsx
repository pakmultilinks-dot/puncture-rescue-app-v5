import { StatusBar } from 'expo-status-bar';
import * as Location from 'expo-location';
import React, { useMemo, useState } from 'react';
import {
  KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View,
} from 'react-native';

type Screen = 'home' | 'area' | 'results' | 'profile' | 'request' | 'listing';
type LocationState = 'idle' | 'checking' | 'denied' | 'checked';
type DemoMechanic = {
  id: string;
  name: string;
  area: string;
  distance: string;
  eta: string;
  availability: string;
  phone: string;
};

const DEMO_MECHANICS: DemoMechanic[] = [
  { id: 'moss', name: 'Moss Lane Puncture Care', area: 'Central sample area', distance: '1.4 km', eta: '12–18 min', availability: 'Sample window: open now', phone: '000 000 0000' },
  { id: 'orbit', name: 'Orbit Wheel Works', area: 'Central sample area', distance: '2.8 km', eta: '20–30 min', availability: 'Sample window: later today', phone: '000 000 0000' },
  { id: 'fern', name: 'Fern Street Tyre Help', area: 'East sample area', distance: '1.9 km', eta: '15–24 min', availability: 'Sample window: open now', phone: '000 000 0000' },
];
const C = {
  paper: '#F6F4EF', white: '#FFFEFB', ink: '#252723', muted: '#62675F', quiet: '#676C63',
  line: '#DAD9D1', accent: '#B94430', alert: '#8B3325',
};

function providersFor(area: string): DemoMechanic[] {
  const value = area.trim().toLowerCase();
  if (value.includes('central') || value.includes('midtown')) return DEMO_MECHANICS.filter((item) => item.id === 'moss' || item.id === 'orbit');
  if (value.includes('east')) return DEMO_MECHANICS.filter((item) => item.id === 'fern');
  return [];
}

function TyreMark() {
  return (
    <View accessible={false} style={styles.markOuter}>
      <View style={styles.markRing} />
      <View style={styles.markRoute} />
      <View style={styles.markDot} />
    </View>
  );
}

function Header({ onHome }: { onHome: () => void }) {
  return (
    <View style={styles.header}>
      <Pressable accessibilityRole="button" accessibilityLabel="Patchlane home" onPress={onHome} style={styles.brand}>
        <TyreMark />
        <Text style={styles.brandName}>Patchlane</Text>
      </Pressable>
      <View accessibilityLabel="Demo · fictional providers and estimates" style={styles.demoPill}>
        <View style={styles.demoDot} />
        <Text style={styles.demoText}>Demo · fictional</Text>
      </View>
    </View>
  );
}

function PrimaryButton({ label, onPress, disabled = false, accessibilityLabel }: {
  label: string; onPress: () => void; disabled?: boolean; accessibilityLabel?: string;
}) {
  return (
    <Pressable
      testID="primary-action"
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || label}
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [styles.primaryButton, pressed && !disabled && styles.pressed, disabled && styles.disabled]}
    >
      <Text style={styles.primaryButtonText}>{label}</Text>
      <Text style={styles.primaryArrow} accessible={false}>→</Text>
    </Pressable>
  );
}

function TextLink({ label, onPress, accessibilityLabel }: {
  label: string; onPress: () => void; accessibilityLabel?: string;
}) {
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={accessibilityLabel || label} onPress={onPress} style={styles.textLink}>
      <Text style={styles.textLinkLabel}>{label}</Text>
      <Text style={styles.linkArrow} accessible={false}>→</Text>
    </Pressable>
  );
}

function BackLink({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={label} onPress={onPress} style={styles.backLink}>
      <Text style={styles.backArrow} accessible={false}>←</Text>
      <Text style={styles.backLabel}>{label}</Text>
    </Pressable>
  );
}

function PageTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <View style={styles.pageTitleBlock}>
      <Text style={styles.pageTitle}>{title}</Text>
      {subtitle ? <Text style={styles.pageSubtitle}>{subtitle}</Text> : null}
    </View>
  );
}

function InlineNote({ children, tone = 'default' }: { children: string; tone?: 'default' | 'alert' }) {
  return (
    <View accessibilityRole={tone === 'alert' ? 'alert' : 'text'} style={styles.inlineNote}>
      <View style={[styles.noteRule, tone === 'alert' && styles.noteRuleAlert]} />
      <Text style={[styles.noteText, tone === 'alert' && styles.noteTextAlert]}>{children}</Text>
    </View>
  );
}

function TextField({ label, value, onChangeText, placeholder, keyboardType = 'default', helper, error }: {
  label: string; value: string; onChangeText: (next: string) => void; placeholder: string;
  keyboardType?: 'default' | 'phone-pad'; helper?: string; error?: string;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={C.quiet}
        keyboardType={keyboardType}
        autoCapitalize={keyboardType === 'phone-pad' ? 'none' : 'words'}
        style={[styles.input, error ? styles.inputError : null]}
      />
      {helper ? <Text style={styles.fieldHelper}>{helper}</Text> : null}
      {error ? <Text accessibilityRole="alert" style={styles.fieldError}>{error}</Text> : null}
    </View>
  );
}

function HomeSteps() {
  return (
    <View accessibilityLabel="Three steps: choose an area, pick a sample mechanic, preview only" style={styles.stepsStrip}>
      <View style={styles.stepItem}>
        <Text style={styles.stepIndex}>01</Text>
        <Text style={styles.stepName}>Area</Text>
        <Text style={styles.stepDetail}>or landmark</Text>
      </View>
      <View style={styles.stepDivider} />
      <View style={styles.stepItem}>
        <Text style={styles.stepIndex}>02</Text>
        <Text style={styles.stepName}>Mechanic</Text>
        <Text style={styles.stepDetail}>sample choices</Text>
      </View>
      <View style={styles.stepDivider} />
      <View style={styles.stepItem}>
        <Text style={styles.stepIndex}>03</Text>
        <Text style={styles.stepName}>Preview</Text>
        <Text style={styles.stepDetail}>nothing sent</Text>
      </View>
    </View>
  );
}

function MechanicRow({ mechanic, onPress }: { mechanic: DemoMechanic; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`Open sample mechanic ${mechanic.name}`}
      onPress={onPress}
      style={({ pressed }) => [styles.mechanicRow, pressed && styles.rowPressed]}
    >
      <View style={styles.mechanicRowTop}>
        <Text style={styles.mechanicName}>{mechanic.name}</Text>
        <View style={styles.rowArrowWrap} accessible={false}><Text style={styles.rowArrow}>↗</Text></View>
      </View>
      <Text style={styles.mechanicArea}>{mechanic.area}</Text>
      <View style={styles.mechanicStats}>
        <View style={styles.mechanicStat}>
          <Text style={styles.statValue}>{mechanic.distance}</Text>
          <Text style={styles.statLabel}>sample distance</Text>
        </View>
        <View style={styles.metaDivider} />
        <View style={styles.mechanicStat}>
          <Text style={styles.statValue}>{mechanic.eta}</Text>
          <Text style={styles.statLabel}>sample ETA</Text>
        </View>
      </View>
      <View style={styles.availabilityLine}>
        <View style={styles.availabilityMark} />
        <Text style={styles.availability}>{mechanic.availability}</Text>
      </View>
    </Pressable>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  );
}

export default function App() {
  const [screen, setScreen] = useState<Screen>('home');
  const [locationState, setLocationState] = useState<LocationState>('idle');
  const [area, setArea] = useState('');
  const [activeArea, setActiveArea] = useState('Central sample area');
  const [message, setMessage] = useState('');
  const [selected, setSelected] = useState<DemoMechanic>(DEMO_MECHANICS[0]);
  const [requestStatus, setRequestStatus] = useState<'waiting' | 'cancelled'>('waiting');
  const [listingName, setListingName] = useState('');
  const [listingPhone, setListingPhone] = useState('');
  const [listingArea, setListingArea] = useState('');
  const [listingErrors, setListingErrors] = useState<Record<string, string>>({});
  const [listingPreview, setListingPreview] = useState(false);
  const mechanics = useMemo(() => providersFor(activeArea), [activeArea]);

  const goHome = () => { setScreen('home'); setMessage(''); };
  const openArea = () => { setMessage(''); setScreen('area'); };
  const showResults = (value: string) => {
    const cleaned = value.trim();
    if (cleaned.length < 2) { setMessage('Enter an area or landmark to continue.'); return; }
    setActiveArea(cleaned);
    setArea(cleaned);
    setMessage('');
    setScreen('results');
  };
  const checkLocationAfterTap = async () => {
    if (locationState === 'checking') return;
    setMessage('');
    setLocationState('checking');
    try {
      const permission = await Location.requestForegroundPermissionsAsync();
      if (permission.status !== 'granted') {
        setLocationState('denied');
        setArea('');
        setScreen('area');
        return;
      }
      // Check one foreground fix, then discard it. The example results never use coordinates.
      await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Low });
      setLocationState('checked');
      setActiveArea('Central sample area');
      setScreen('results');
    } catch {
      setLocationState('denied');
      setArea('');
      setScreen('area');
    }
  };
  const openMechanic = (mechanic: DemoMechanic) => { setSelected(mechanic); setMessage(''); setScreen('profile'); };
  const validateListing = () => {
    const errors: Record<string, string> = {};
    if (listingName.trim().length < 2) errors.name = 'Enter a fictional name with at least two characters.';
    if (listingPhone.replace(/\D/g, '') !== '0000000000') errors.phone = 'Use the all-zero sample number: 000 000 0000.';
    if (listingArea.trim().length < 2) errors.area = 'Enter a sample coverage area.';
    setListingErrors(errors);
    setListingPreview(Object.keys(errors).length === 0);
  };

  const renderHome = () => (
    <ScrollView contentContainerStyle={[styles.content, styles.homeContent]} showsVerticalScrollIndicator={false}>
      <View style={styles.homeIntro}>
        <Text style={styles.kicker}>Motorcycle puncture help</Text>
        <Text style={styles.homeTitle}>Flat tyre?{ '\n' }Find a mechanic.</Text>
        <Text style={styles.homeSubtitle}>Find puncture help through your area or a familiar landmark.</Text>
      </View>
      <HomeSteps />
      <InlineNote>Location is checked once, only after you tap. It is never shared.</InlineNote>
      <View style={styles.homeActions}>
        <PrimaryButton
          label={locationState === 'checking' ? 'Checking location…' : 'Find puncture help'}
          accessibilityLabel="Find puncture help using optional one-time location check"
          onPress={checkLocationAfterTap}
          disabled={locationState === 'checking'}
        />
        <TextLink label="Use an area or landmark" onPress={openArea} />
      </View>
      <Pressable accessibilityRole="button" accessibilityLabel="Mechanic or shop? Preview one shared listing" onPress={() => { setListingErrors({}); setListingPreview(false); setScreen('listing'); }} style={styles.listingInvite}>
        <View style={styles.inviteRule} />
        <View style={styles.inviteCopy}>
          <Text style={styles.inviteTitle}>Mechanic or shop?</Text>
          <Text style={styles.inviteSubtitle}>Preview one shared listing</Text>
        </View>
        <Text style={styles.rowArrow} accessible={false}>↗</Text>
      </Pressable>
    </ScrollView>
  );

  const renderArea = () => (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">
      <BackLink label="Back" onPress={goHome} />
      <PageTitle title="Where should we look?" subtitle={locationState === 'denied' ? 'Location was not available. Enter an area or landmark instead.' : 'Enter an area or landmark to see sample mechanics.'} />
      <TextField label="Area or landmark" value={area} onChangeText={(value) => { setArea(value); setMessage(''); }} placeholder="e.g., Central sample area" helper="Try Central sample area or East sample area." error={message} />
      <PrimaryButton label="Show sample mechanics" onPress={() => showResults(area)} />
    </ScrollView>
  );

  const renderResults = () => (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <BackLink label={mechanics.length ? 'Change area' : 'Back to start'} onPress={mechanics.length ? openArea : goHome} />
      <PageTitle title={mechanics.length ? 'Sample mechanics' : 'No sample mechanics yet'} subtitle={activeArea} />
      <InlineNote>Examples · not matched to your location. Distance, timing and availability are fictional.</InlineNote>
      {mechanics.length ? (
        <View style={styles.mechanicList}>
          {mechanics.map((mechanic) => <MechanicRow key={mechanic.id} mechanic={mechanic} onPress={() => openMechanic(mechanic)} />)}
        </View>
      ) : (
        <View style={styles.emptyState}>
          <View style={styles.emptyMark}><TyreMark /></View>
          <Text style={styles.emptyEyebrow}>NO MATCH IN THIS SAMPLE</Text>
          <Text style={styles.emptyText}>No sample listings in {activeArea}. Try Central or East sample area.</Text>
          <PrimaryButton label="Change area" onPress={openArea} />
        </View>
      )}
    </ScrollView>
  );

  const renderProfile = () => (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <BackLink label="Sample mechanics" onPress={() => setScreen('results')} />
      <View style={styles.profileHeading}>
        <View style={styles.profileMark}><TyreMark /></View>
        <PageTitle title={selected.name} subtitle={selected.area} />
      </View>
      <View style={styles.detailList}>
        <DetailRow label="Sample distance" value={`${selected.distance} · example`} />
        <DetailRow label="Sample ETA" value={selected.eta} />
        <DetailRow label="Availability" value={selected.availability} />
        <DetailRow label="Sample phone" value={selected.phone} />
      </View>
      <InlineNote>Fictional profile. No call can be placed from this preview.</InlineNote>
      <PrimaryButton label="Preview request" onPress={() => { setRequestStatus('waiting'); setScreen('request'); }} />
    </ScrollView>
  );

  const renderRequest = () => (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <BackLink label="Mechanic details" onPress={() => setScreen('profile')} />
      <PageTitle title="Request preview" subtitle="Motorcycle puncture help" />
      <View style={styles.requestStatus}>
        <View style={[styles.statusDot, requestStatus === 'cancelled' && styles.statusDotQuiet]} />
        <View style={styles.requestStatusCopy}>
          <Text style={styles.requestStatusEyebrow}>LOCAL PREVIEW</Text>
          <Text style={styles.requestStatusTitle}>{requestStatus === 'waiting' ? 'Waiting for a reply' : 'Preview cancelled'}</Text>
          <Text style={styles.requestStatusSub}>{requestStatus === 'waiting' ? 'Simulated · no mechanic was contacted' : 'Nothing was sent or shared'}</Text>
        </View>
      </View>
      <View style={styles.detailList}>
        <DetailRow label="Mechanic" value={selected.name} />
        <DetailRow label="Sample area" value={activeArea} />
      </View>
      <PrimaryButton
        label={requestStatus === 'waiting' ? 'Cancel request preview' : 'Back to sample mechanics'}
        onPress={() => requestStatus === 'waiting' ? setRequestStatus('cancelled') : setScreen('results')}
      />
    </ScrollView>
  );

  const renderListing = () => (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">
      <BackLink label="Back" onPress={goHome} />
      <PageTitle title="Preview a listing" subtitle="One form for an individual mechanic or a shop." />
      {listingPreview ? <InlineNote>No listing was saved, published or sent.</InlineNote> : null}
      <View style={styles.form}>
        <TextField label="Name riders will see" value={listingName} onChangeText={(value) => { setListingName(value); setListingPreview(false); }} placeholder="Sample Wheel Help" error={listingErrors.name} />
        <TextField label="Sample phone number" value={listingPhone} onChangeText={(value) => { setListingPhone(value); setListingPreview(false); }} placeholder="000 000 0000" keyboardType="phone-pad" helper="Use the all-zero sample number only." error={listingErrors.phone} />
        <TextField label="Sample coverage area" value={listingArea} onChangeText={(value) => { setListingArea(value); setListingPreview(false); }} placeholder="Central sample area" error={listingErrors.area} />
      </View>
      {listingPreview ? <View style={styles.listingPreview}>
        <Text style={styles.previewLabel}>Preview only</Text>
        <Text style={styles.listingPreviewName}>{listingName.trim()}</Text>
        <Text style={styles.previewDetail}>{listingArea.trim()} · 000 000 0000</Text>
      </View> : null}
      <PrimaryButton label={listingPreview ? 'Edit details' : 'Preview listing'} onPress={listingPreview ? () => setListingPreview(false) : validateListing} />
    </ScrollView>
  );

  return (
    <View style={styles.app}>
      <StatusBar style="dark" />
      <View style={styles.shell}>
        <Header onHome={goHome} />
        <KeyboardAvoidingView style={styles.pageContainer} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
          {screen === 'home' ? renderHome() : null}
          {screen === 'area' ? renderArea() : null}
          {screen === 'results' ? renderResults() : null}
          {screen === 'profile' ? renderProfile() : null}
          {screen === 'request' ? renderRequest() : null}
          {screen === 'listing' ? renderListing() : null}
        </KeyboardAvoidingView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  app: { flex: 1, minHeight: '100%', backgroundColor: C.paper },
  shell: { flex: 1, width: '100%', maxWidth: 520, alignSelf: 'center', backgroundColor: C.paper },
  header: { minHeight: 68, paddingHorizontal: 23, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderBottomWidth: 1, borderBottomColor: C.line },
  brand: { minHeight: 50, flexDirection: 'row', alignItems: 'center', gap: 10 },
  brandName: { color: C.ink, fontSize: 17, fontWeight: '700', letterSpacing: -0.25 },
  markOuter: { width: 31, height: 31, borderRadius: 16, borderWidth: 1.5, borderColor: C.ink, alignItems: 'center', justifyContent: 'center' },
  markRing: { width: 17, height: 17, borderRadius: 9, borderWidth: 2, borderColor: C.accent },
  markRoute: { position: 'absolute', width: 17, height: 2, borderRadius: 2, backgroundColor: C.ink, transform: [{ rotate: '-44deg' }], left: 15, top: 14 },
  markDot: { position: 'absolute', width: 4, height: 4, borderRadius: 2, backgroundColor: C.accent, left: 8, top: 8 },
  demoPill: { minHeight: 34, paddingHorizontal: 10, borderRadius: 18, borderWidth: 1, borderColor: C.line, flexDirection: 'row', alignItems: 'center', gap: 6 },
  demoDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: C.accent },
  demoText: { color: C.muted, fontSize: 11, fontWeight: '600', letterSpacing: 0.05 },
  pageContainer: { flex: 1, minHeight: 0 },
  content: { flexGrow: 1, paddingHorizontal: 24, paddingTop: 23, paddingBottom: 34, gap: 21 },
  homeContent: { paddingTop: 29, gap: 0 },
  homeIntro: { gap: 12, marginBottom: 20 },
  kicker: { color: C.accent, fontSize: 12, lineHeight: 18, fontWeight: '700', letterSpacing: 1.15, textTransform: 'uppercase' },
  homeTitle: { color: C.ink, fontFamily: 'Georgia', fontSize: 37, lineHeight: 43, fontWeight: '700', letterSpacing: -0.75 },
  homeSubtitle: { color: C.muted, fontSize: 16, lineHeight: 24, maxWidth: 318 },
  stepsStrip: { minHeight: 78, flexDirection: 'row', alignItems: 'center', borderTopWidth: 1, borderBottomWidth: 1, borderColor: C.line, paddingVertical: 11, marginBottom: 18 },
  stepItem: { flex: 1, minWidth: 0, gap: 2, paddingHorizontal: 6 },
  stepIndex: { color: C.accent, fontSize: 11, lineHeight: 14, fontWeight: '700', letterSpacing: 0.75 },
  stepName: { color: C.ink, fontSize: 13, lineHeight: 17, fontWeight: '700' },
  stepDetail: { color: C.muted, fontSize: 11, lineHeight: 15 },
  stepDivider: { width: 1, height: 38, backgroundColor: C.line },
  inlineNote: { flexDirection: 'row', alignItems: 'stretch', gap: 11, marginBottom: 18 },
  noteRule: { width: 2, minHeight: 24, borderRadius: 2, backgroundColor: C.accent, marginVertical: 2 },
  noteRuleAlert: { backgroundColor: C.alert },
  noteText: { flex: 1, color: C.muted, fontSize: 14, lineHeight: 21 },
  noteTextAlert: { color: C.alert },
  homeActions: { alignItems: 'center' },
  primaryButton: { width: '100%', minHeight: 58, paddingHorizontal: 18, borderRadius: 14, backgroundColor: C.accent, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 12 },
  primaryButtonText: { color: C.white, fontSize: 16, lineHeight: 21, fontWeight: '700', textAlign: 'center' },
  primaryArrow: { position: 'absolute', right: 18, color: C.white, fontSize: 20, fontWeight: '500' },
  pressed: { opacity: 0.8 },
  disabled: { opacity: 0.55 },
  textLink: { minHeight: 50, minWidth: 48, paddingHorizontal: 10, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8 },
  textLinkLabel: { color: C.ink, fontSize: 14, fontWeight: '600' },
  linkArrow: { color: C.accent, fontSize: 16 },
  listingInvite: { minHeight: 70, marginTop: 25, paddingTop: 15, borderTopWidth: 1, borderTopColor: C.line, flexDirection: 'row', alignItems: 'center', gap: 13 },
  inviteRule: { width: 3, height: 34, borderRadius: 2, backgroundColor: C.accent },
  inviteCopy: { flex: 1, gap: 4 },
  inviteTitle: { color: C.ink, fontSize: 15, fontWeight: '600' },
  inviteSubtitle: { color: C.muted, fontSize: 13, lineHeight: 18 },
  backLink: { minHeight: 48, minWidth: 48, alignSelf: 'flex-start', paddingHorizontal: 2, flexDirection: 'row', alignItems: 'center', gap: 9 },
  backArrow: { color: C.accent, fontSize: 19, lineHeight: 22 },
  backLabel: { color: C.muted, fontSize: 14, fontWeight: '600' },
  pageTitleBlock: { gap: 9 },
  pageTitle: { color: C.ink, fontFamily: 'Georgia', fontSize: 31, lineHeight: 37, fontWeight: '700', letterSpacing: -0.45 },
  pageSubtitle: { color: C.muted, fontSize: 15, lineHeight: 22 },
  field: { gap: 8 },
  fieldLabel: { color: C.ink, fontSize: 14, lineHeight: 19, fontWeight: '600' },
  input: { width: '100%', minHeight: 56, paddingHorizontal: 15, borderRadius: 12, borderWidth: 1, borderColor: C.line, backgroundColor: C.white, color: C.ink, fontSize: 16, lineHeight: 22 },
  inputError: { borderColor: C.alert },
  fieldHelper: { color: C.muted, fontSize: 13, lineHeight: 19 },
  fieldError: { color: C.alert, fontSize: 13, lineHeight: 19 },
  mechanicList: { marginTop: -3 },
  mechanicRow: { minHeight: 144, paddingVertical: 17, borderBottomWidth: 1, borderBottomColor: C.line, justifyContent: 'center', gap: 7 },
  rowPressed: { opacity: 0.64 },
  mechanicRowTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  mechanicName: { flex: 1, color: C.ink, fontSize: 18, lineHeight: 24, fontWeight: '600' },
  rowArrowWrap: { width: 28, height: 28, borderRadius: 14, borderWidth: 1, borderColor: C.line, alignItems: 'center', justifyContent: 'center' },
  rowArrow: { color: C.accent, fontSize: 19, lineHeight: 23 },
  mechanicArea: { color: C.muted, fontSize: 14, lineHeight: 19 },
  mechanicStats: { flexDirection: 'row', alignItems: 'center', gap: 15, marginTop: 2 },
  mechanicStat: { minWidth: 76, gap: 1 },
  statValue: { color: C.ink, fontSize: 14, lineHeight: 18, fontWeight: '700' },
  statLabel: { color: C.muted, fontSize: 11, lineHeight: 15 },
  metaDivider: { width: 1, height: 29, backgroundColor: C.line },
  availabilityLine: { flexDirection: 'row', alignItems: 'center', gap: 7 },
  availabilityMark: { width: 6, height: 6, borderRadius: 3, backgroundColor: C.accent },
  availability: { color: C.muted, fontSize: 12, lineHeight: 17 },
  emptyState: { gap: 12, marginTop: 8 },
  emptyMark: { width: 54, height: 54, borderRadius: 27, backgroundColor: '#EFE8E2', alignItems: 'center', justifyContent: 'center', marginBottom: 2 },
  emptyEyebrow: { color: C.accent, fontSize: 11, lineHeight: 15, fontWeight: '700', letterSpacing: 1.05 },
  emptyText: { color: C.muted, fontSize: 16, lineHeight: 24, marginBottom: 4 },
  profileHeading: { gap: 16 },
  profileMark: { width: 42, height: 42, alignItems: 'center', justifyContent: 'center' },
  detailList: { borderTopWidth: 1, borderTopColor: C.line },
  detailRow: { minHeight: 56, paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: C.line, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 15 },
  detailLabel: { flex: 1, color: C.muted, fontSize: 14, lineHeight: 20 },
  detailValue: { maxWidth: '62%', color: C.ink, fontSize: 14, lineHeight: 20, fontWeight: '600', textAlign: 'right' },
  requestStatus: { minHeight: 94, paddingVertical: 13, paddingHorizontal: 14, borderTopWidth: 1, borderBottomWidth: 1, borderLeftWidth: 3, borderColor: C.line, borderLeftColor: C.accent, backgroundColor: '#EFE8E2', flexDirection: 'row', alignItems: 'center', gap: 13 },
  statusDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: C.accent },
  statusDotQuiet: { backgroundColor: C.quiet },
  requestStatusCopy: { flex: 1, gap: 3 },
  requestStatusEyebrow: { color: C.ink, fontSize: 10, lineHeight: 14, fontWeight: '700', letterSpacing: 1 },
  requestStatusTitle: { color: C.ink, fontSize: 17, lineHeight: 22, fontWeight: '600' },
  requestStatusSub: { color: C.muted, fontSize: 13, lineHeight: 18 },
  form: { gap: 20 },
  listingPreview: { paddingTop: 16, borderTopWidth: 1, borderTopColor: C.line, gap: 6 },
  previewLabel: { color: C.accent, fontSize: 14, fontWeight: '600' },
  listingPreviewName: { color: C.ink, fontSize: 18, lineHeight: 24, fontWeight: '600' },
  previewDetail: { color: C.muted, fontSize: 14, lineHeight: 20 },
});
