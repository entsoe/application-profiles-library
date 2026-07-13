#!perl -w
use strict;
use warnings;
use Text::CSV_XS;

my $csv_file = 'shacl-sparql.csv';
my $prefixes = 'prefixes.rq';
my $outdir   = 'shacl-sparql';

mkdir $outdir unless -d $outdir;

my $prefix_text = do {
    open my $pfh, '<:encoding(UTF-8)', $prefixes or die "Cannot open $prefixes: $!";
    local $/;
    <$pfh>;
};

my $csv = Text::CSV_XS->new({ binary => 1, auto_diag => 1 });

open my $fh, '<:encoding(UTF-8)', $csv_file or die "Cannot open $csv_file: $!";
my $header = $csv->getline($fh);   # shape,shapeLocalname,descr,sparql

open my $stats, '>:encoding(UTF-8)', 'shacl-sparql-stats.tsv' or die "Cannot write stats: $!";
print $stats "name\tchars\tlines\n";

while (my $row = $csv->getline($fh)) {
    my ($shape, $name, $descr, $sparql) = @$row;
    next unless defined $name && $name ne '';

    $sparql //= '';
    my $chars = length $sparql;
    my $lines = () = $sparql =~ /\n/g;
    $lines++ if length $sparql && $sparql !~ /\n\z/;
    print $stats "$name\t$chars\t$lines\n";

    open my $out, '>:encoding(UTF-8)', "$outdir/$name.rq" or die "Cannot write $name.rq: $!";
    print $out "# $shape\n";
    print $out "# $name\n";
    print $out "# ", ($descr // ''), "\n";
    print $out "\n";
    print $out $prefix_text;
    print $out "\n";
    print $out $sparql;
    close $out;
}
close $fh;
close $stats;
