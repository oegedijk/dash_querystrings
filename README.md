# Dash querystring example

Natively Dash (dash.plot.ly) does not support saving the state in the url.

This is unfortunate, as when you are creating a dashboard of some kind you
often want your users to be able to share it easily. The easiest way to do this
is by making shareable urls that conserve and recreate the state of the dash app.

This code shows an example how you can save the state of a Dash app in
the querystring, and then reload the state of the app from a given url.

Also shows how you can use pyshortener to provide tinyurls that are more
easily passed around the office.

Based on [this github gist](https://gist.github.com/jtpio/1aeb0d850dcd537a5b244bcf5aeaa75b),
but added support for :

1. Other parameters than just 'value'
2. Multiple parameters per component
3. Lists as values

Plus: an example of how to turn long urls into tiny urls inside dash.

# querystring_methods
## 1. `encode_state(component_ids_zipped, values)`:

Returns a querystring encoding the state defined by `component_ids_zipped`
and `values`.

Takes a list of component id's (`compnent_ids_zipped[0]`), a list of component
parameters (`component_ids_zipped[1]`) and a list of `values` for these
parameters.

It first turns it into a format that `urllib.parse.urlencode()` can work with,
and then encodes it.

## 2. `parse_state(url)`:

Returns a dictionary with the the component id as key, and a list of
(parameter, value) pairs as the item.

When the first character of the value is a '[', then parse the value using
`ast.literal_eval()`.

In case it looks like  number (int or float) parse it accordingly.

## 3. `apply_value_from_querystring(params)`:

You wrap this around the definition of your component in your layout definition,
and then on page load it automatically sets the value saved in the query string
(and parsed into params), as the default value for the specific parameters for
that component id.

`params` is in the form of a dictionary return by `parse_state(url)`.

You wrap it around the component definition like this:

```
apply_value_from_querystring(params)(dcc.RadioItems)(
        id='country_radiobutton',
        options=[{'label': i, 'value': i}
                    for i in ['Canada', 'USA', 'Mexico']],
        value='Canada'
    ),
```
